#!/usr/bin/env python3
"""normalize_capture.py — evdev capture (jsonl) → mapper-neutral event stream.

The mapper-conversion lab's **event normalizer** (plan §5): folds a raw
`evdev_capture.py --jsonl` dump into a canonical, press-paired, mapper-neutral
event list with timestamps relative to the first event — the form the eventual
comparator diffs across the JSM and Steam lanes. Pure preparatory infrastructure:
it transforms captures, it does NOT emit configs, equivalence rules, or KB entries.

Input line schema (from evdev_capture.py): {"t","dev","type","code","value"}.
`type` ∈ KEY|REL|ABS|SYN. SYN is dropped. KEY/BTN down(1)/up(0) are paired into
press records with a duration; REL is aggregated per axis.

Canonical names (mapper-neutral): KEY_<X> -> <X> ; BTN_LEFT/RIGHT/MIDDLE ->
MOUSE_LEFT/RIGHT/MIDDLE ; other BTN_<X> -> <X> ; REL_X/Y -> MOUSE_DX/DY ;
REL_WHEEL/HWHEEL -> WHEEL/HWHEEL.

Usage:
  normalize_capture.py CAPTURE.jsonl [--json OUT.json] [--pretty]

NOTE: XI2 (Steam-lane) captures use a different jsonl schema; XI2 normalization is
a follow-up to add once the Steam lane produces data (the canonical vocabulary here
is designed to receive it).
"""
import argparse
import json
import sys


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


def normalize(lines):
    raw = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            raw.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    raw = [e for e in raw if e.get("type") != "SYN"]
    if not raw:
        return {"n_raw": 0, "events": [], "summary": {"presses": {}, "rel_totals": {}}}
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
        key = (e["dev"], e["code"])
        if e["value"] == 1:  # down
            open_presses[key] = (e["t"], name, kind)
        elif e["value"] == 0:  # up
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
        "n_raw": len(raw),
        "t0_epoch": t0,
        "events": events,
        "summary": {"presses": press_counts, "rel_totals": rel_totals},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture", help="evdev_capture.py --jsonl file (or - for stdin)")
    ap.add_argument("--json", help="write the normalized JSON here")
    ap.add_argument("--pretty", action="store_true", help="print a human-readable event table")
    args = ap.parse_args()

    src = sys.stdin if args.capture == "-" else open(args.capture)
    with src:
        norm = normalize(src)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(norm, f, indent=2)
    if args.pretty or not args.json:
        s = norm["summary"]
        print(f"# {norm['n_raw']} raw events  presses={s['presses']}  rel_totals={s['rel_totals']}")
        for ev in norm["events"]:
            dur = "" if ev.get("dur_ms") is None else f"  {ev['dur_ms']:.0f}ms"
            note = f"  [{ev['note']}]" if ev.get("note") else ""
            val = f"  val={ev['value']}" if ev["kind"] == "rel" else ""
            print(f"  +{ev['t_ms']:>8.1f}ms  {ev['kind']:<9} {ev['name']}{dur}{val}{note}")


if __name__ == "__main__":
    sys.exit(main())
