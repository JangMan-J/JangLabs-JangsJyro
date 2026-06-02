#!/usr/bin/env python3
"""synthetic_gamepad.py — create a synthetic uinput gamepad and inject a scripted
button/trigger sequence, for driving a mapper (JSM / Steam Input) without the
physical controller.

This is the **synthetic input provider** the mapper-conversion lab needs for the
Phase 1 tracer bullet and Phase 2 quick-wins (mapper-conversion-lab-plan.md §5,
§10). It presents a standard Xbox-360-layout evdev device (vendor 045e:028e,
"Microsoft X-Box 360 pad") so SDL classifies it as a gamepad via its built-in
mapping — the cheapest "will SDL/JSM see a synthetic pad at all?" probe. The
native-8BitDo `uhid` spoof (needed for *gyro*, R2) is a separate, later escalation.

Usage:
  synthetic_gamepad.py --warmup 8 --linger 5 [--repeat 1] [--name NAME] \
                       [--vendor 0x045e] [--product 0x028e] [--log FILE]

It prints (and optionally logs) a timestamped line for every injected action so a
parallel evdev/XI2 capture of the mapper's OUTPUT can be aligned to the stimulus.
Requires rw on /dev/uinput (python-evdev). Holds the device open for
warmup+sequence+linger seconds, then destroys it cleanly.
"""
import argparse
import sys
import time
from datetime import datetime, timezone

from evdev import UInput, AbsInfo, ecodes as e

XBOX360_KEYS = [
    e.BTN_SOUTH, e.BTN_EAST, e.BTN_NORTH, e.BTN_WEST,
    e.BTN_TL, e.BTN_TR, e.BTN_SELECT, e.BTN_START, e.BTN_MODE,
    e.BTN_THUMBL, e.BTN_THUMBR,
]
STICK = AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)
TRIG = AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)
HAT = AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)
XBOX360_ABS = [
    (e.ABS_X, STICK), (e.ABS_Y, STICK), (e.ABS_RX, STICK), (e.ABS_RY, STICK),
    (e.ABS_Z, TRIG), (e.ABS_RZ, TRIG),
    (e.ABS_HAT0X, HAT), (e.ABS_HAT0Y, HAT),
]

_logf = None


def log(msg):
    now = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    mono = time.monotonic()
    line = f"[{now}Z mono={mono:.3f}] {msg}"
    print(line, flush=True)
    if _logf:
        _logf.write(line + "\n")
        _logf.flush()


def main():
    global _logf
    ap = argparse.ArgumentParser()
    ap.add_argument("--warmup", type=float, default=8.0,
                    help="seconds to hold the device idle before injecting (lets the mapper enumerate it)")
    ap.add_argument("--linger", type=float, default=5.0,
                    help="seconds to keep the device alive after the sequence")
    ap.add_argument("--repeat", type=int, default=1, help="repeat the press/trigger sequence N times")
    ap.add_argument("--name", default="Microsoft X-Box 360 pad")
    ap.add_argument("--vendor", default="0x045e")
    ap.add_argument("--product", default="0x028e")
    ap.add_argument("--version", default="0x0114")
    ap.add_argument("--log", default=None, help="append timestamped action log to this file too")
    args = ap.parse_args()

    if args.log:
        _logf = open(args.log, "a")

    cap = {e.EV_KEY: XBOX360_KEYS, e.EV_ABS: XBOX360_ABS}
    ui = UInput(cap, name=args.name,
                vendor=int(args.vendor, 0), product=int(args.product, 0),
                version=int(args.version, 0), bustype=e.BUS_USB)
    try:
        log(f"CREATED uinput gamepad name={args.name!r} {args.vendor}:{args.product} -> {ui.device.path if ui.device else '?'}")
        log(f"WARMUP {args.warmup}s (mapper should enumerate the pad now)")
        time.sleep(args.warmup)

        for i in range(args.repeat):
            # South face button (JSM cardinal 'S' = SDL SOUTH = Xbox 'A')
            log(f"[{i}] BTN_SOUTH down")
            ui.write(e.EV_KEY, e.BTN_SOUTH, 1); ui.syn()
            time.sleep(0.120)
            log(f"[{i}] BTN_SOUTH up")
            ui.write(e.EV_KEY, e.BTN_SOUTH, 0); ui.syn()
            time.sleep(0.400)

            # Right trigger (JSM 'ZR' fires off the ABS_RZ analog threshold)
            log(f"[{i}] ABS_RZ ramp 0->255 (right trigger pull)")
            for v in range(0, 256, 32):
                ui.write(e.EV_ABS, e.ABS_RZ, v); ui.syn()
                time.sleep(0.012)
            ui.write(e.EV_ABS, e.ABS_RZ, 255); ui.syn()
            time.sleep(0.200)
            log(f"[{i}] ABS_RZ ramp 255->0 (right trigger release)")
            for v in range(255, -1, -32):
                ui.write(e.EV_ABS, e.ABS_RZ, max(v, 0)); ui.syn()
                time.sleep(0.012)
            ui.write(e.EV_ABS, e.ABS_RZ, 0); ui.syn()
            time.sleep(0.400)

        log(f"SEQUENCE done; LINGER {args.linger}s")
        time.sleep(args.linger)
    finally:
        log("DESTROY uinput device")
        ui.close()
        if _logf:
            _logf.close()


if __name__ == "__main__":
    sys.exit(main())
