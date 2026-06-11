#!/usr/bin/env python3
"""normalize_capture.py — evdev / xi2 capture (jsonl) → mapper-neutral event stream.

The mapper-conversion lab's **event normalizer** (plan §5): folds a raw
`evdev_capture.py --jsonl` or `xi2_capture.py capture --jsonl` dump into a
canonical, press-paired, mapper-neutral event list with timestamps relative to
the first event — the form the eventual comparator diffs across the JSM and
Steam lanes. Pure preparatory infrastructure: it transforms captures, it does
NOT emit configs, equivalence rules, or KB entries.

Evdev input line schema (from evdev_capture.py):
  {"t","dev","type","code","value"}
  `type` ∈ KEY|REL|ABS|SYN. SYN is dropped. KEY/BTN down(1)/up(0) are paired
  into press records with a duration; REL is aggregated per axis.

XI2 input line schema (from xi2_capture.py):
  {"t","event","dev_id","dev","code","flag"}
  `event` ∈ KeyPress|KeyRelease|RawKeyPress|RawKeyRelease|ButtonPress|…
  Raw* events (from the master/virtual device) are deduplicated — when both a
  Raw and a Device event carry the same code close in time, only the Device
  event (KeyPress/KeyRelease from the xwayland-keyboard seat) is kept.
  Keysym fold: L1→F11, L2→F12 (legacy X keysym names for those F-keys).

Canonical names (mapper-neutral):
  evdev:  KEY_<X> -> <X> ; BTN_LEFT/RIGHT/MIDDLE -> MOUSE_LEFT/RIGHT/MIDDLE ;
          other BTN_<X> -> <X> ; REL_X/Y -> MOUSE_DX/DY ; REL_WHEEL -> WHEEL
  xi2:    keysym name used directly (already canonical: F9, F10, Return, …)
          after keysym fold (L1→F11, L2→F12).

Usage:
  normalize_capture.py CAPTURE.jsonl [--json OUT.json] [--pretty]
                       [--plane {evdev,xi2}]

The plane is auto-detected from the first non-empty record (evdev records have a
"type" field; xi2 records have an "event" field).  Pass --plane to override.
"""
import argparse
import json
import sys

# XI2 keysym fold: legacy names that xinput prints for certain F-keys
_XI2_KEYSYM_FOLD: dict[str, str] = {
    "L1": "F11",
    "L2": "F12",
}

# XI2 events that represent the "device" (xwayland-seat) plane — use these
# for press-pairing. Raw* events from the master virtual device are duplicates.
_XI2_PRESS_EVENTS = {"KeyPress", "ButtonPress"}
_XI2_RELEASE_EVENTS = {"KeyRelease", "ButtonRelease"}
_XI2_RAW_EVENTS = {"RawKeyPress", "RawKeyRelease", "RawButtonPress", "RawButtonRelease"}

# Dedup window: if a Device event and a Raw event carry the same code within
# this many seconds of each other, the Raw event is the duplicate.
_DEDUP_WINDOW_S = 0.005  # 5 ms


def canon(code: str) -> tuple[str, str]:
    """(kind, canonical_name) for an evdev code string."""
    if code.startswith("KEY_"):
        return "key", code[4:]
    if code in ("BTN_LEFT", "BTN_RIGHT", "BTN_MIDDLE"):
        return "mousebtn", "MOUSE_" + code[4:]
    if code in ("BTN_SIDE", "BTN_EXTRA", "BTN_FORWARD", "BTN_BACK"):
        return "mousebtn", "MOUSE_" + code[4:]
    if code.startswith("BTN_"):
        return "button", code[4:]
    if code == "REL_X":
        return "rel", "MOUSE_DX"
    if code == "REL_Y":
        return "rel", "MOUSE_DY"
    if code == "REL_WHEEL":
        return "rel", "WHEEL"
    if code == "REL_HWHEEL":
        return "rel", "HWHEEL"
    if code.startswith("REL_"):
        return "rel", code[4:]
    return "other", code


def _detect_plane(records: list[dict]) -> str:
    """Return 'xi2' if records look like xi2_capture output, else 'evdev'."""
    for r in records:
        if "event" in r and "type" not in r:
            return "xi2"
        if "type" in r:
            return "evdev"
    return "evdev"


def _xi2_canon(code: str) -> tuple[str, str]:
    """(kind, canonical_name) for an xi2 keysym/button code string."""
    code = _XI2_KEYSYM_FOLD.get(code, code)
    if code.startswith("BTN_"):
        return "mousebtn", "MOUSE_" + code[4:]
    if code.startswith("btn"):
        return "mousebtn", code.upper()
    if code in ("WHEEL_UP", "WHEEL_DOWN", "WHEEL_LEFT", "WHEEL_RIGHT"):
        return "rel", code
    return "key", code


def normalize_xi2(records: list[dict]) -> dict:
    """Normalize an XI2 capture record list into the canonical event stream.

    Dedup: Raw* events from the master/virtual-core device are duplicates of
    the Device (KeyPress/KeyRelease) events on the xwayland-seat — keep only
    the Device events.  The 'deduped-raw' note is attached to skipped Raws so
    they show in n_raw but not events.

    Keysym fold: L1→F11, L2→F12.

    Press-pairing: KeyPress/ButtonPress open a record; KeyRelease/ButtonRelease
    close it with dur_ms.  The pairing key is (dev_id, code) to handle
    multiple XI2 devices in the same stream.
    """
    if not records:
        return {"schema_version": "1", "plane": "xi2", "n_raw": 0,
                "t0_epoch": None, "events": [],
                "summary": {"presses": {}, "rel_totals": {}}}

    # Dedup: for each code, track the Device-event timestamps so we can
    # identify and skip Raw events within the dedup window.
    device_timestamps: dict[str, list[float]] = {}
    deduped_raw_set: set[int] = set()  # indices into records
    for i, r in enumerate(records):
        ev = r.get("event", "")
        code = _XI2_KEYSYM_FOLD.get(r.get("code", ""), r.get("code", ""))
        if ev in _XI2_PRESS_EVENTS or ev in _XI2_RELEASE_EVENTS:
            device_timestamps.setdefault(code, []).append(r["t"])
    for i, r in enumerate(records):
        ev = r.get("event", "")
        if ev not in _XI2_RAW_EVENTS:
            continue
        code = _XI2_KEYSYM_FOLD.get(r.get("code", ""), r.get("code", ""))
        times = device_timestamps.get(code, [])
        if any(abs(r["t"] - dt) <= _DEDUP_WINDOW_S for dt in times):
            deduped_raw_set.add(i)

    n_raw = len(records)
    t0 = min(r["t"] for r in records)
    ms = lambda t: round((t - t0) * 1000.0, 1)

    events = []
    open_presses: dict[tuple, tuple] = {}  # (dev_id, code) -> (t_down, name, kind)
    rel_totals: dict[str, float] = {}
    press_counts: dict[str, int] = {}

    for i, r in enumerate(records):
        ev = r.get("event", "")
        if i in deduped_raw_set:
            continue  # Raw duplicate — counted in n_raw but not emitted
        raw_code = r.get("code", "")
        code = _XI2_KEYSYM_FOLD.get(raw_code, raw_code)
        kind, name = _xi2_canon(code)
        dev_id = r.get("dev_id")

        if kind == "rel":
            val = 1 if "UP" in code or "RIGHT" in code else -1
            rel_totals[name] = rel_totals.get(name, 0) + val
            events.append({"kind": "rel", "name": name, "t_ms": ms(r["t"]), "value": val})
            continue

        if ev in _XI2_RAW_EVENTS:
            # Unmatched Raw event (no Device counterpart within window) — treat as noise
            continue

        key = (dev_id, code)
        if ev in _XI2_PRESS_EVENTS:
            open_presses[key] = (r["t"], name, kind)
        elif ev in _XI2_RELEASE_EVENTS:
            if key in open_presses:
                td, nm, kd = open_presses.pop(key)
                events.append({"kind": kd, "name": nm, "t_ms": ms(td),
                               "dur_ms": round((r["t"] - td) * 1000.0, 1)})
                press_counts[nm] = press_counts.get(nm, 0) + 1
            else:
                events.append({"kind": kind, "name": name, "t_ms": ms(r["t"]),
                               "dur_ms": None, "note": "up-only"})

    for key, (td, nm, kd) in open_presses.items():
        events.append({"kind": kd, "name": nm, "t_ms": ms(td),
                       "dur_ms": None, "note": "still-held-at-end"})
        press_counts[nm] = press_counts.get(nm, 0) + 1

    events.sort(key=lambda x: x["t_ms"])
    return {
        "schema_version": "1",
        "plane": "xi2",
        "n_raw": n_raw,
        "t0_epoch": t0,
        "events": events,
        "summary": {"presses": press_counts, "rel_totals": rel_totals},
    }


def normalize(lines, plane: str = "auto") -> dict:
    """Parse JSONL lines and normalize into the canonical event stream.

    plane: 'evdev', 'xi2', or 'auto' (detect from first record).
    Returns the normalized stream dict (schema_version + plane fields added).
    Evdev output is backward-compatible with the original format but gains
    schema_version and plane keys.
    """
    raw = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            raw.append(json.loads(ln))
        except json.JSONDecodeError:
            continue

    if plane == "auto":
        plane = _detect_plane(raw)

    if plane == "xi2":
        return normalize_xi2(raw)

    # evdev path (original logic, extended with schema_version/plane)
    raw = [e for e in raw if e.get("type") != "SYN"]
    if not raw:
        return {"schema_version": "1", "plane": "evdev",
                "n_raw": 0, "events": [],
                "summary": {"presses": {}, "rel_totals": {}}}
    t0 = min(e["t"] for e in raw)
    ms = lambda t: round((t - t0) * 1000.0, 1)

    events = []
    open_presses = {}  # (dev, code) -> (t_down, name, kind)
    rel_totals = {}
    press_counts = {}
    for e in raw:
        kind, name = canon(e["code"])
        if kind == "rel":
            rel_totals[name] = rel_totals.get(name, 0) + int(e["value"])
            events.append({"kind": "rel", "name": name, "t_ms": ms(e["t"]), "value": int(e["value"])})
            continue
        key = (e.get("dev", ""), e["code"])
        val = e.get("value")
        if val is None:  # not a valid evdev press record — skip
            continue
        if val == 1:  # down
            open_presses[key] = (e["t"], name, kind)
        elif val == 0:  # up
            if key in open_presses:
                td, nm, kd = open_presses.pop(key)
                events.append({"kind": kd, "name": nm, "t_ms": ms(td),
                               "dur_ms": round((e["t"] - td) * 1000.0, 1)})
                press_counts[nm] = press_counts.get(nm, 0) + 1
            else:  # up with no matching down (capture started mid-press)
                events.append({"kind": kind, "name": name, "t_ms": ms(e["t"]), "dur_ms": None, "note": "up-only"})
    for key, (td, nm, kd) in open_presses.items():  # still held at capture end
        events.append({"kind": kd, "name": nm, "t_ms": ms(td), "dur_ms": None, "note": "still-held-at-end"})
        press_counts[nm] = press_counts.get(nm, 0) + 1
    events.sort(key=lambda x: x["t_ms"])
    return {
        "schema_version": "1",
        "plane": "evdev",
        "n_raw": len(raw),
        "t0_epoch": t0,
        "events": events,
        "summary": {"presses": press_counts, "rel_totals": rel_totals},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture", help="capture JSONL file (evdev or xi2), or - for stdin")
    ap.add_argument("--json", help="write the normalized JSON here")
    ap.add_argument("--pretty", action="store_true", help="print a human-readable event table")
    ap.add_argument("--plane", choices=["evdev", "xi2", "auto"], default="auto",
                    help="observation plane (default: auto-detect from first record)")
    args = ap.parse_args()

    src = sys.stdin if args.capture == "-" else open(args.capture)
    with src:
        norm = normalize(src, plane=args.plane)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(norm, f, indent=2)
    if args.pretty or not args.json:
        s = norm["summary"]
        plane_tag = norm.get("plane", "evdev")
        print(f"# [{plane_tag}] {norm['n_raw']} raw events  "
              f"presses={s['presses']}  rel_totals={s['rel_totals']}")
        for ev in norm["events"]:
            dur = "" if ev.get("dur_ms") is None else f"  {ev['dur_ms']:.0f}ms"
            note = f"  [{ev['note']}]" if ev.get("note") else ""
            val = f"  val={ev['value']}" if ev["kind"] == "rel" else ""
            print(f"  +{ev['t_ms']:>8.1f}ms  {ev['kind']:<9} {ev['name']}{dur}{val}{note}")


if __name__ == "__main__":
    sys.exit(main())
