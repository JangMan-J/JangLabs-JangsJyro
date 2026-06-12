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

# Canonical key namespace: both evdev and xi2 output must speak ONE vocabulary
# so the comparator can compare role-aligned key names directly.
#
# evdev: canon() strips KEY_ then applies this table.
# xi2:   _xi2_canon() applies this table after keysym fold.
# Single lowercase letters (a-z) are uppercased by the xi2 path without a table entry.
_CANON_KEY_FOLD: dict[str, str] = {
    # Shift
    "LEFTSHIFT":  "LSHIFT",
    "RIGHTSHIFT": "RSHIFT",
    # Ctrl
    "LEFTCTRL":   "LCTRL",
    "RIGHTCTRL":  "RCTRL",
    # Alt
    "LEFTALT":    "LALT",
    "RIGHTALT":   "RALT",
    # Meta/Super
    "LEFTMETA":   "LMETA",
    "RIGHTMETA":  "RMETA",
}

# XI2 modifier keysym -> canonical name (applied before _CANON_KEY_FOLD lookup)
_XI2_MOD_FOLD: dict[str, str] = {
    "Shift_L":   "LSHIFT",
    "Shift_R":   "RSHIFT",
    "Control_L": "LCTRL",
    "Control_R": "RCTRL",
    "Alt_L":     "LALT",
    "Alt_R":     "RALT",
    "Meta_L":    "LMETA",
    "Meta_R":    "RMETA",
    "Super_L":   "LMETA",
    "Super_R":   "RMETA",
}

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
        name = code[4:]
        return "key", _CANON_KEY_FOLD.get(name, name)
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
    """(kind, canonical_name) for an xi2 keysym/button code string.

    Fold order:
      1. _XI2_MOD_FOLD: Shift_L -> LSHIFT, Control_L -> LCTRL, etc.
      2. _XI2_KEYSYM_FOLD: L1 -> F11, L2 -> F12.
      3. Lowercase single letter (a-z) -> uppercase (Steam emits 'q'; JSM emits 'Q').
      4. Button/wheel classification.
    """
    # Modifier fold first (takes precedence over everything else)
    if code in _XI2_MOD_FOLD:
        return "key", _XI2_MOD_FOLD[code]
    # Legacy F-key keysym fold
    code = _XI2_KEYSYM_FOLD.get(code, code)
    # Uppercase single lowercase letters (Steam emits e.g. 'q', 'w', 'a', 'd')
    if len(code) == 1 and code.islower():
        code = code.upper()
    if code.startswith("BTN_"):
        return "mousebtn", "MOUSE_" + code[4:]
    if code.startswith("btn"):
        return "mousebtn", code.upper()
    if code in ("WHEEL_UP", "WHEEL_DOWN", "WHEEL_LEFT", "WHEEL_RIGHT"):
        return "rel", code
    return "key", code


def normalize_xi2(records: list[dict]) -> dict:
    """Normalize an XI2 capture record list into the canonical event stream.

    Timing model (per finding runs/20260612T053331Z-phase4-pin-batch1/result.md §P2):
    Steam SI via EIS/Xwayland sends raw-layer tap pairs: RawKeyPress immediately
    followed by RawKeyRelease, fired atomically at the SI emission moment.  The
    key/slave layer (KeyPress/KeyRelease) is a flush-on-next-event delivery queue
    whose timestamps reflect queue-flush points, NOT SI emission points.  Raw-layer
    timestamps are the correct timing reference for all oracle-pin calculations.

    This function uses RawKeyPress timestamps for t_down and RawKeyRelease
    timestamps for t_up/dur_ms.  Key-layer (Device) events are used only as a
    fallback when no matching Raw event is present (e.g. captures from non-SI
    sources that emit only Device events).

    Dedup: Raw* events that have a matching Device event within the dedup window
    are counted in n_raw but suppressed from the output events — the Raw provides
    the timing, the Device provides the pairing signal.  Unmatched Raw events
    (no Device counterpart) are treated as noise and also suppressed.

    Keysym fold: L1→F11, L2→F12.

    Press-pairing: RawKeyPress opens a record (using raw timestamp); RawKeyRelease
    (or KeyRelease if no Raw available) closes it with dur_ms.  The pairing key is
    (code,) — Raw events don't carry dev_id, so we pair by code alone at the raw
    layer, then resolve the press record when the matching Device release arrives.
    """
    if not records:
        return {"schema_version": "1", "plane": "xi2", "n_raw": 0,
                "t0_epoch": None, "events": [],
                "summary": {"presses": {}, "rel_totals": {}}}

    # Dedup pass: identify Raw events that have a corresponding Device event
    # within the dedup window (they are duplicates of the Device plane).
    device_timestamps: dict[str, list[float]] = {}
    deduped_raw_set: set[int] = set()  # indices into records
    for i, r in enumerate(records):
        ev = r.get("event", "")
        raw_code: str = r.get("code") or ""
        code: str = _XI2_KEYSYM_FOLD.get(raw_code, raw_code)
        if ev in _XI2_PRESS_EVENTS or ev in _XI2_RELEASE_EVENTS:
            device_timestamps.setdefault(code, []).append(r["t"])
    for i, r in enumerate(records):
        ev = r.get("event", "")
        if ev not in _XI2_RAW_EVENTS:
            continue
        raw_code = r.get("code") or ""
        code = _XI2_KEYSYM_FOLD.get(raw_code, raw_code)
        times = device_timestamps.get(code, [])
        if any(abs(r["t"] - dt) <= _DEDUP_WINDOW_S for dt in times):
            deduped_raw_set.add(i)

    n_raw = len(records)
    t0 = min(r["t"] for r in records)
    ms = lambda t: round((t - t0) * 1000.0, 1)

    # Raw-layer timestamp index: code -> [t, ...] for press and release separately.
    # Used to override key-layer timestamps with raw-layer emission times.
    raw_press_times: dict[str, list[float]] = {}   # code -> list of raw-down timestamps
    raw_release_times: dict[str, list[float]] = {}  # code -> list of raw-up timestamps
    for i, r in enumerate(records):
        ev = r.get("event", "")
        raw_code = r.get("code") or ""
        code = _XI2_KEYSYM_FOLD.get(raw_code, raw_code)
        if ev == "RawKeyPress":
            raw_press_times.setdefault(code, []).append(r["t"])
        elif ev == "RawKeyRelease":
            raw_release_times.setdefault(code, []).append(r["t"])

    events = []
    open_presses: dict[tuple, tuple] = {}  # (dev_id, code) -> (t_down, name, kind)
    rel_totals: dict[str, float] = {}
    press_counts: dict[str, int] = {}

    # Consume-pointer for raw timestamp queues (FIFO per code).
    raw_press_idx: dict[str, int] = {}
    raw_release_idx: dict[str, int] = {}

    for i, r in enumerate(records):
        ev = r.get("event", "")
        if i in deduped_raw_set:
            continue  # Raw duplicate — counted in n_raw but not emitted
        raw_code = r.get("code") or ""
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
            # Use the raw-layer press timestamp if available (FIFO: consume oldest).
            raw_times = raw_press_times.get(code, [])
            idx = raw_press_idx.get(code, 0)
            if idx < len(raw_times):
                t_down = raw_times[idx]
                raw_press_idx[code] = idx + 1
            else:
                t_down = r["t"]  # fallback: no raw event for this key
            open_presses[key] = (t_down, name, kind)
        elif ev in _XI2_RELEASE_EVENTS:
            if key in open_presses:
                td, nm, kd = open_presses.pop(key)
                # Use the raw-layer release timestamp if available.
                raw_rel = raw_release_times.get(code, [])
                ridx = raw_release_idx.get(code, 0)
                if ridx < len(raw_rel):
                    t_up = raw_rel[ridx]
                    raw_release_idx[code] = ridx + 1
                else:
                    t_up = r["t"]  # fallback
                events.append({"kind": kd, "name": nm, "t_ms": ms(td),
                               "dur_ms": round((t_up - td) * 1000.0, 1)})
                press_counts[nm] = press_counts.get(nm, 0) + 1
            else:
                events.append({"kind": kind, "name": name, "t_ms": ms(r["t"]),
                               "dur_ms": None, "note": "up-only"})

    for key, (td, nm, kd) in open_presses.items():
        events.append({"kind": kd, "name": nm, "t_ms": ms(td),
                       "dur_ms": None, "note": "still-held-at-end"})
        press_counts[nm] = press_counts.get(nm, 0) + 1

    # Emit raw-only press pairs that were never claimed by a Device event.
    # This handles Release_Press's combined-instant emission: Steam emits a
    # RawKeyPress + RawKeyRelease atomically with no Device counterpart (or
    # one that arrives outside the capture window).  Without this step, such
    # events would be silently dropped as "unmatched raw noise" above.
    for code, press_list in raw_press_times.items():
        consumed_press = raw_press_idx.get(code, 0)
        consumed_rel = raw_release_idx.get(code, 0)
        rel_list = raw_release_times.get(code, [])
        _, name = _xi2_canon(code)
        for j in range(consumed_press, len(press_list)):
            td = press_list[j]
            rel_j = consumed_rel + (j - consumed_press)
            if rel_j < len(rel_list):
                t_up = rel_list[rel_j]
                dur = round((t_up - td) * 1000.0, 1)
                events.append({"kind": "key", "name": name, "t_ms": ms(td),
                               "dur_ms": dur})
            else:
                # Press with no matching raw release — still-held at end
                events.append({"kind": "key", "name": name, "t_ms": ms(td),
                               "dur_ms": None, "note": "still-held-at-end"})
            press_counts[name] = press_counts.get(name, 0) + 1

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
