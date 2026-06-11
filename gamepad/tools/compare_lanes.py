#!/usr/bin/env python3
"""compare_lanes.py — compare two normalized streams (one per lane) and emit
delta + classification artifacts (plan §14 Chunk B).

Takes two normalized-stream dicts (from normalize_capture.py) and optional
key_roles dicts from the run manifests, then produces:
  - a delta dict (per the delta schema)
  - a classification dict (per the classification schema)

Design (v1 — generic role-aligned core):

  Both streams are normalized to the CANONICAL KEY NAMESPACE by normalize_capture.py
  (evdev KEY_LEFTSHIFT → LSHIFT; xi2 Shift_L → LSHIFT; xi2 lowercase 'q' → Q).
  In Phase-9 production the converter emits the same key names as the Steam reference,
  so the normal case is key-name equality with no alignment needed.

  For Phase-2 characterization captures (JSM and Steam authored independently with
  different key names), the run manifests carry key_roles:
    {"jsm": {"tap": "A", "hold": "B"}, "steam": {"tap": "F10", "hold": "F11"}}
  Roles without a listing default to identity (role == key name) — this is the
  Phase-9 production default and requires no manifest entry.

  GENERIC CORE:
    1. Build a role→events map from each lane's filtered stream and its roles dict.
    2. For each role, compare event-sequences (count, duration model, order) across
       lanes; emit delta-fact entries.
    3. Map the combined delta-fact set to a verdict via a small mechanic-keyed
       pattern table.  Mechanic-specific knowledge lives in the manifests (roles)
       and in the verdict-pattern table below — not in per-mechanic plugin classes.

Usage:
  compare_lanes.py --jsm JSM_NORM.json --steam STEAM_NORM.json
                   --mechanic MECHANIC_NAME
                   [--jsm-roles '{"tap":"A","hold":"B"}']
                   [--steam-roles '{"tap":"F10","hold":"F11"}']
                   [--jsm-manifest JSM_RUN_MANIFEST.json]
                   [--steam-manifest STEAM_RUN_MANIFEST.json]
                   [--out-delta DELTA.json]
                   [--out-class CLASSIFICATION.json]
                   [--pretty]

Tests: tools/test_compare_lanes.py (stdlib unittest, no deps).
"""
import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Core primitives — work on a flat list of press events
# ---------------------------------------------------------------------------

def _press_events(norm: dict) -> list[dict]:
    """Extract press-paired events (kind != 'rel') from a normalized stream."""
    return [e for e in norm.get("events", []) if e.get("kind") != "rel"]


def _press_counts(events: list[dict]) -> dict[str, int]:
    """name -> count of completed presses (excludes still-held-at-end, up-only)."""
    c: dict[str, int] = {}
    for e in events:
        if e.get("note") in ("still-held-at-end", "up-only"):
            continue
        c[e["name"]] = c.get(e["name"], 0) + 1
    return c


def _distinct_keys(events: list[dict]) -> list[str]:
    """Distinct key names in order of first appearance."""
    seen: list[str] = []
    for e in events:
        if e["name"] not in seen:
            seen.append(e["name"])
    return seen


# ---------------------------------------------------------------------------
# Role-based alignment
# ---------------------------------------------------------------------------


def _events_for_key(events: list[dict], key_name: str) -> list[dict]:
    """All events whose name matches key_name (case-sensitive after namespace fold)."""
    return [e for e in events if e["name"] == key_name]


def _role_events(norm: dict, roles: dict[str, str],
                 allowlist: set[str] | None = None) -> dict[str, list[dict]]:
    """Build role -> [events] from a normalized stream + roles mapping.

    If roles is empty (identity case), each key name is its own role.
    If allowlist is given, only events with names in allowlist are considered
    (used as a noise filter when roles are specified — roles take precedence).
    """
    all_evs = _press_events(norm)
    if roles:
        result: dict[str, list[dict]] = {}
        for role, key_name in roles.items():
            result[role] = _events_for_key(all_evs, key_name)
        return result
    # No roles: filter by allowlist if provided, then each key is its own role
    if allowlist:
        all_evs = [e for e in all_evs if e["name"] in allowlist]
    counts = _press_counts(all_evs)
    return {k: [e for e in all_evs if e["name"] == k] for k in counts}


# ---------------------------------------------------------------------------
# Delta-entry builder
# ---------------------------------------------------------------------------

def _entry(kind: str, name: str, delta_type: str,
           jsm_val=None, steam_val=None, note: str | None = None) -> dict:
    e: dict = {"kind": kind, "name": name, "delta_type": delta_type,
               "jsm_value": jsm_val, "steam_value": steam_val}
    if note:
        e["note"] = note
    return e


# ---------------------------------------------------------------------------
# Generic delta-fact emitter
# ---------------------------------------------------------------------------

def _emit_role_deltas(role: str,
                      jsm_evs: list[dict],
                      steam_evs: list[dict]) -> list[dict]:
    """Compare two role-aligned event lists and emit delta-fact entries.

    Delta types used:
      jsm-only    — role present in JSM but not Steam (or Steam count << JSM)
      steam-only  — role present in Steam but not JSM
      count-differs — both have presses but counts differ
      dur-differs   — both have the role but duration model differs
    """
    entries: list[dict] = []
    j_counts = _press_counts(jsm_evs)
    s_counts = _press_counts(steam_evs)
    j_total = sum(j_counts.values())
    s_total = sum(s_counts.values())

    # Presence delta
    if j_total > 0 and s_total == 0:
        entries.append(_entry("key", role, "jsm-only",
                               j_total, 0,
                               f"Role '{role}' present in JSM but absent in Steam"))
    elif s_total > 0 and j_total == 0:
        entries.append(_entry("key", role, "steam-only",
                               0, s_total,
                               f"Role '{role}' present in Steam but absent in JSM"))
    elif j_total != s_total:
        entries.append(_entry("key", role, "count-differs",
                               j_total, s_total,
                               f"Role '{role}' press count differs"))

    # Note: duration deltas are intentionally NOT emitted here.
    # Timing parameters (HOLD_PRESS_TIME, Long Press Time, etc.) differ by design
    # between JSM and Steam — those are Phase-4 characterization material, not
    # structural comparator signals.  The comparator compares press-shape (presence,
    # count, order) not absolute durations.

    return entries


# ---------------------------------------------------------------------------
# Mechanic-level verdict pattern table
#
# Each entry: mechanic -> list of (condition_fn, verdict, loss_text)
# condition_fn(delta_entries, jsm_roles, steam_roles) -> bool
# The FIRST matching condition wins.  Final fallback: no entries -> exact.
# ---------------------------------------------------------------------------

def _has_jsm_only(entries: list[dict]) -> bool:
    return any(e["delta_type"] == "jsm-only" for e in entries)


def _has_steam_only(entries: list[dict]) -> bool:
    return any(e["delta_type"] == "steam-only" for e in entries)


def _has_count_differs(entries: list[dict]) -> bool:
    return any(e["delta_type"] == "count-differs" for e in entries)


def _has_any_delta(entries: list[dict]) -> bool:
    return len(entries) > 0


# Pattern table: mechanic -> list of (predicate, verdict, loss_text)
# Predicates operate on (entries, jsm_role_events, steam_role_events).
# They receive the full delta entry list for the mechanic.
_VERDICT_PATTERNS: dict[str, list[tuple]] = {
    "digital": [
        # Any structural delta (extra keys, missing presses) -> degraded
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Digital press model structural mismatch"),
    ],
    "taphold": [
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Tap/hold model structural mismatch"),
    ],
    "doublepress": [
        # JSM fires base on 1st press of pair:
        #   - base role is jsm-only (pure presence delta), OR
        #   - base role count-differs with jsm > steam (extra base press on JSM)
        # Both signal the same known delta -> bounded_approximation.
        (lambda e, _j, _s: _has_jsm_only(e) or any(
             en["delta_type"] == "count-differs"
             and int(en.get("jsm_value") or 0) > int(en.get("steam_value") or 0)
             for en in e),
         "bounded_approximation",
         "JSM fires base binding on first press of a double pair; "
         "Steam suppresses base entirely when second press lands inside Double Tap Time. "
         "Steam→JSM adds extra base keystroke; JSM→Steam loses first-press echo."),
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Double-press structural mismatch"),
    ],
    "chord": [
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Chord structural mismatch"),
    ],
    "simpress": [
        # Steam leaks member binding (steam-only role) or JSM sticky (jsm-only count) -> degraded
        (lambda e, _j, _s: _has_steam_only(e) or _has_jsm_only(e),
         "degraded_approximation",
         "Steam leaks chord member's regular binding (fires alongside chord output). "
         "JSM SIMPRESS suppresses both members. JSM also has sticky-state bug: "
         "lone press after chord re-emits chord binding. No Steam counterpart."),
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Simultaneous-press structural mismatch"),
    ],
    "simpress2": [
        (lambda e, _j, _s: _has_steam_only(e) or _has_jsm_only(e),
         "degraded_approximation",
         "Steam leaks chord member's regular binding; JSM sticky-state re-emits chord binding."),
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Simultaneous-press structural mismatch"),
    ],
    "trigfull": [
        (lambda e, _j, _s: _has_any_delta(e),
         "bounded_approximation",
         "Trigger soft/full structural mismatch"),
    ],
    "stickwasd": [
        (lambda e, _j, _s: _has_any_delta(e),
         "degraded_approximation",
         "Stick-WASD structural mismatch"),
    ],
}


def _apply_patterns(mechanic: str,
                    entries: list[dict],
                    jsm_role_evs: dict[str, list[dict]],
                    steam_role_evs: dict[str, list[dict]]) -> tuple[str, str | None]:
    """Return (verdict, loss_text) by applying the mechanic's pattern table."""
    patterns = _VERDICT_PATTERNS.get(mechanic, [])
    for pred, verdict, loss_text in patterns:
        if pred(entries, jsm_role_evs, steam_role_evs):
            return verdict, loss_text
    return "exact", None


# ---------------------------------------------------------------------------
# Public compare() entry point
# ---------------------------------------------------------------------------

def compare(mechanic: str,
            jsm_norm: dict, steam_norm: dict,
            jsm_keys: set[str] | None = None,
            steam_keys: set[str] | None = None,
            jsm_roles: dict[str, str] | None = None,
            steam_roles: dict[str, str] | None = None,
            jsm_run: str = "",
            steam_run: str = "") -> tuple[dict, dict]:
    """Compare two normalized streams for the given mechanic.

    jsm_roles / steam_roles: optional role->canonical-key-name dicts from
    the run manifests.  Identity (role==key) when absent — the Phase-9 default.

    jsm_keys / steam_keys: legacy allowlist filter (used when no roles are
    available, e.g. in unit tests that don't supply manifest data).  When roles
    are given, roles take precedence and allowlists are ignored.

    Returns (delta_dict, classification_dict) conforming to the schemas.
    """
    # Build role->events from each lane
    jsm_role_evs = _role_events(jsm_norm,
                                 jsm_roles or {},
                                 allowlist=jsm_keys if not jsm_roles else None)
    stm_role_evs = _role_events(steam_norm,
                                 steam_roles or {},
                                 allowlist=steam_keys if not steam_roles else None)

    # Gather all roles present in either lane
    all_roles = list(dict.fromkeys(list(jsm_role_evs) + list(stm_role_evs)))

    # Emit delta facts per role
    entries: list[dict] = []
    for role in all_roles:
        j_evs = jsm_role_evs.get(role, [])
        s_evs = stm_role_evs.get(role, [])
        entries.extend(_emit_role_deltas(role, j_evs, s_evs))

    # Extra structural checks for digital: only 1 distinct key per lane; ≥1 press per lane.
    # Cross-lane count differences are intentionally NOT checked for digital — JSM and Steam
    # captures come from different run sessions with different stimulus counts.  "Exact" for
    # digital means each lane independently has 1 key and ≥1 completed press, not that both
    # lanes have the same literal count.
    if mechanic == "digital":
        # Remove any count-differs entries emitted above (from _emit_role_deltas) — those
        # are only meaningful for mechanics where cross-lane count equality is expected.
        entries = [e for e in entries if e["delta_type"] != "count-differs"]

        j_all = _press_events(jsm_norm)
        s_all = _press_events(steam_norm)
        if jsm_keys and not jsm_roles:
            j_all = [e for e in j_all if e["name"] in jsm_keys]
        if steam_keys and not steam_roles:
            s_all = [e for e in s_all if e["name"] in steam_keys]
        if jsm_roles:
            j_all = [e for es in jsm_role_evs.values() for e in es]
        if steam_roles:
            s_all = [e for es in stm_role_evs.values() for e in es]
        j_distinct = _distinct_keys(j_all)
        s_distinct = _distinct_keys(s_all)
        j_total = sum(_press_counts(j_all).values())
        s_total = sum(_press_counts(s_all).values())
        if len(j_distinct) > 1:
            entries.append(_entry("key", "<digital-extra-keys>", "jsm-only",
                                   len(j_distinct), 1,
                                   f"JSM has unexpected extra keys: {j_distinct}"))
        if len(s_distinct) > 1:
            entries.append(_entry("key", "<digital-extra-keys>", "steam-only",
                                   1, len(s_distinct),
                                   f"Steam has unexpected extra keys: {s_distinct}"))
        if j_total == 0:
            entries.append(_entry("key", "<digital>", "jsm-only",
                                   0, s_total, "JSM lane has no presses for the expected key"))
        if s_total == 0:
            entries.append(_entry("key", "<digital>", "steam-only",
                                   j_total, 0, "Steam lane has no presses for the expected key"))

    verdict, loss_text = _apply_patterns(mechanic, entries,
                                          jsm_role_evs, stm_role_evs)

    # Build summaries
    j_counts_all = {role: sum(_press_counts(evs).values())
                    for role, evs in jsm_role_evs.items() if evs}
    s_counts_all = {role: sum(_press_counts(evs).values())
                    for role, evs in stm_role_evs.items() if evs}

    delta = {
        "schema_version": "1",
        "mechanic": mechanic,
        "jsm_run": jsm_run,
        "steam_run": steam_run,
        "entries": entries,
    }
    classification = {
        "schema_version": "1",
        "mechanic": mechanic,
        "verdict": verdict,
        "loss_text": loss_text,
        "jsm_summary": f"JSM roles={j_counts_all}",
        "steam_summary": f"Steam roles={s_counts_all}",
        "evidence_refs": [],
        "notes": None,
    }
    return delta, classification


# ---------------------------------------------------------------------------
# Helpers for loading roles from a run manifest
# ---------------------------------------------------------------------------

def roles_from_manifest(manifest_path: str | Path, slice_name: str,
                         lane: str) -> dict[str, str]:
    """Extract key_roles[lane] for a given slice from a run manifest JSON.

    Returns an empty dict if the manifest has no key_roles for this slice/lane
    (identity default — role == key name).
    """
    with open(manifest_path) as f:
        manifest = json.load(f)
    for s in manifest.get("slices", []):
        if s.get("slice") == slice_name:
            kr = s.get("key_roles") or {}
            return dict(kr.get(lane, {}))
    return {}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jsm", required=True, help="JSM-lane normalized stream JSON")
    ap.add_argument("--steam", required=True, help="Steam-lane normalized stream JSON")
    ap.add_argument("--mechanic", required=True,
                    help="Mechanic name (e.g. taphold, doublepress, chord, …)")
    ap.add_argument("--jsm-roles",
                    help="JSON object mapping role->key-name for the JSM lane "
                         "(e.g. '{\"tap\":\"A\",\"hold\":\"B\"}')")
    ap.add_argument("--steam-roles",
                    help="JSON object mapping role->key-name for the Steam lane")
    ap.add_argument("--jsm-keys", help="Comma-separated allowlist of JSM key names "
                    "(fallback when no roles; ignored if --jsm-roles given)")
    ap.add_argument("--steam-keys", help="Comma-separated allowlist of Steam key names")
    ap.add_argument("--jsm-manifest",
                    help="JSM run manifest JSON — roles and evidence_refs loaded from here")
    ap.add_argument("--steam-manifest",
                    help="Steam run manifest JSON — roles and evidence_refs loaded from here")
    ap.add_argument("--out-delta", help="Write delta artifact JSON here")
    ap.add_argument("--out-class", help="Write classification artifact JSON here")
    ap.add_argument("--pretty", action="store_true", help="Print human-readable summary")
    args = ap.parse_args(argv)

    with open(args.jsm) as f:
        jsm_norm = json.load(f)
    with open(args.steam) as f:
        steam_norm = json.load(f)

    jsm_roles: dict[str, str] | None = None
    steam_roles: dict[str, str] | None = None

    if args.jsm_roles:
        jsm_roles = json.loads(args.jsm_roles)
    elif args.jsm_manifest:
        jsm_roles = roles_from_manifest(args.jsm_manifest, args.mechanic, "jsm") or None

    if args.steam_roles:
        steam_roles = json.loads(args.steam_roles)
    elif args.steam_manifest:
        steam_roles = roles_from_manifest(args.steam_manifest, args.mechanic, "steam") or None

    jsm_keys = set(args.jsm_keys.split(",")) if args.jsm_keys else None
    steam_keys = set(args.steam_keys.split(",")) if args.steam_keys else None

    jsm_run = str(Path(args.jsm).parent) if not args.jsm_manifest else \
              str(Path(args.jsm_manifest).parent)
    steam_run = str(Path(args.steam).parent) if not args.steam_manifest else \
                str(Path(args.steam_manifest).parent)

    delta, classification = compare(
        args.mechanic, jsm_norm, steam_norm,
        jsm_keys=jsm_keys, steam_keys=steam_keys,
        jsm_roles=jsm_roles, steam_roles=steam_roles,
        jsm_run=jsm_run, steam_run=steam_run,
    )

    if args.out_delta:
        with open(args.out_delta, "w") as f:
            json.dump(delta, f, indent=2)
    if args.out_class:
        with open(args.out_class, "w") as f:
            json.dump(classification, f, indent=2)
    if args.pretty or (not args.out_delta and not args.out_class):
        v = classification["verdict"]
        print(f"mechanic={args.mechanic}  verdict={v}")
        print(f"  jsm:   {classification['jsm_summary']}")
        print(f"  steam: {classification['steam_summary']}")
        if delta["entries"]:
            print(f"  delta entries ({len(delta['entries'])}):")
            for e in delta["entries"]:
                print(f"    [{e['delta_type']}] {e['name']}: "
                      f"jsm={e.get('jsm_value')} steam={e.get('steam_value')}"
                      + (f"  # {e.get('note', '')}" if e.get("note") else ""))
        else:
            print("  delta: (none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
