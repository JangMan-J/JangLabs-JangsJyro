#!/usr/bin/env python3
"""synthetic_gamepad.py — synthetic uinput gamepad + scriptable trace runner.

The mapper-conversion lab's **synthetic input provider + trace runner** (plan §5):
presents a standard Xbox-360-layout evdev device (vendor 045e:028e, "Microsoft
X-Box 360 pad") that SDL classifies as a gamepad via its built-in mapping, then
either replays a built-in demo sequence or a **trace file** (a small DSL), so a
mapper (JSM / Steam Input) can be driven with no physical controller. The
native-8BitDo `uhid` spoof (needed for *gyro*, R2) is a separate later escalation.

Every injected action prints a timestamped line (and optionally appends to --log)
so a parallel evdev/XI2 capture of the mapper's OUTPUT aligns to the stimulus.

Usage:
  synthetic_gamepad.py [--warmup S] [--linger S] [--repeat N] [--log FILE]
  synthetic_gamepad.py --trace TRACE.txt [--warmup S] [--linger S] [--log FILE]

Trace DSL (one action per line; '#' comments; blanks ignored):
  wait <ms>                 sleep ms
  down <BTN>                press a button (no release)
  up <BTN>                  release a button
  press <BTN> [ms=120]      down, wait ms, up
  axis <NAME> <value>       set an absolute axis (raw evdev value), then SYN
  Buttons: SOUTH EAST NORTH WEST TL TR SELECT START MODE THUMBL THUMBR
  Axes:    LX LY RX RY (sticks, -32768..32767)  LZ RZ (triggers, 0..255)
           HX HY (dpad hat, -1..1)
  (--warmup wraps before the trace; --linger after; the device is destroyed last.)

Requires rw on /dev/uinput (python-evdev).
"""
import argparse
import sys
import time
from datetime import datetime, timezone

from evdev import UInput, AbsInfo, ecodes as e

BTN = {
    "SOUTH": e.BTN_SOUTH, "EAST": e.BTN_EAST, "NORTH": e.BTN_NORTH, "WEST": e.BTN_WEST,
    "TL": e.BTN_TL, "TR": e.BTN_TR, "SELECT": e.BTN_SELECT, "START": e.BTN_START,
    "MODE": e.BTN_MODE, "THUMBL": e.BTN_THUMBL, "THUMBR": e.BTN_THUMBR,
}
AXIS = {
    "LX": e.ABS_X, "LY": e.ABS_Y, "RX": e.ABS_RX, "RY": e.ABS_RY,
    "LZ": e.ABS_Z, "RZ": e.ABS_RZ, "HX": e.ABS_HAT0X, "HY": e.ABS_HAT0Y,
}
STICK = AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)
TRIG = AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)
HAT = AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)
CAP = {
    e.EV_KEY: list(BTN.values()),
    e.EV_ABS: [(e.ABS_X, STICK), (e.ABS_Y, STICK), (e.ABS_RX, STICK), (e.ABS_RY, STICK),
               (e.ABS_Z, TRIG), (e.ABS_RZ, TRIG), (e.ABS_HAT0X, HAT), (e.ABS_HAT0Y, HAT)],
}

_logf = None


def log(msg):
    now = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    line = f"[{now}Z mono={time.monotonic():.3f}] {msg}"
    print(line, flush=True)
    if _logf:
        _logf.write(line + "\n"); _logf.flush()


def do_action(ui, parts):
    op = parts[0].lower()
    if op == "wait":
        ms = float(parts[1]); log(f"wait {ms}ms"); time.sleep(ms / 1000.0)
    elif op == "down":
        b = parts[1].upper(); log(f"down {b}"); ui.write(e.EV_KEY, BTN[b], 1); ui.syn()
    elif op == "up":
        b = parts[1].upper(); log(f"up {b}"); ui.write(e.EV_KEY, BTN[b], 0); ui.syn()
    elif op == "press":
        b = parts[1].upper(); ms = float(parts[2]) if len(parts) > 2 else 120.0
        log(f"press {b} {ms}ms (down)"); ui.write(e.EV_KEY, BTN[b], 1); ui.syn()
        time.sleep(ms / 1000.0)
        log(f"press {b} (up)"); ui.write(e.EV_KEY, BTN[b], 0); ui.syn()
    elif op == "axis":
        a = parts[1].upper(); v = int(parts[2]); log(f"axis {a}={v}")
        ui.write(e.EV_ABS, AXIS[a], v); ui.syn()
    else:
        log(f"WARN unknown action: {' '.join(parts)}")


def replay(ui, trace_path):
    log(f"REPLAY trace {trace_path}")
    with open(trace_path) as f:
        for raw in f:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            do_action(ui, line.split())


def demo(ui, repeat):
    for i in range(repeat):
        do_action(ui, ["press", "SOUTH", "120"]); time.sleep(0.4)
        log(f"[{i}] ABS_RZ ramp 0->255");
        for v in range(0, 256, 32):
            ui.write(e.EV_ABS, e.ABS_RZ, v); ui.syn(); time.sleep(0.012)
        ui.write(e.EV_ABS, e.ABS_RZ, 255); ui.syn(); time.sleep(0.2)
        log(f"[{i}] ABS_RZ ramp 255->0")
        for v in range(255, -1, -32):
            ui.write(e.EV_ABS, e.ABS_RZ, max(v, 0)); ui.syn(); time.sleep(0.012)
        ui.write(e.EV_ABS, e.ABS_RZ, 0); ui.syn(); time.sleep(0.4)


def main():
    global _logf
    ap = argparse.ArgumentParser()
    ap.add_argument("--warmup", type=float, default=8.0)
    ap.add_argument("--linger", type=float, default=5.0)
    ap.add_argument("--repeat", type=int, default=1, help="demo-sequence repeats (ignored with --trace)")
    ap.add_argument("--trace", default=None, help="replay this trace DSL file instead of the demo sequence")
    ap.add_argument("--name", default="Microsoft X-Box 360 pad")
    ap.add_argument("--vendor", default="0x045e")
    ap.add_argument("--product", default="0x028e")
    ap.add_argument("--version", default="0x0114")
    ap.add_argument("--log", default=None)
    args = ap.parse_args()

    if args.log:
        _logf = open(args.log, "a")
    ui = UInput(CAP, name=args.name, vendor=int(args.vendor, 0), product=int(args.product, 0),
                version=int(args.version, 0), bustype=e.BUS_USB)
    try:
        log(f"CREATED pad name={args.name!r} {args.vendor}:{args.product} -> {ui.device.path if ui.device else '?'}")
        log(f"WARMUP {args.warmup}s")
        time.sleep(args.warmup)
        if args.trace:
            replay(ui, args.trace)
        else:
            demo(ui, args.repeat)
        log(f"SEQUENCE done; LINGER {args.linger}s")
        time.sleep(args.linger)
    finally:
        log("DESTROY pad")
        ui.close()
        if _logf:
            _logf.close()


if __name__ == "__main__":
    sys.exit(main())
