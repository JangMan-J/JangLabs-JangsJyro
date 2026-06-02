# gamepad

Gamepad input investigations on the 8BitDo Ultimate 2 Wireless. This research lab lives as a subdirectory inside the JangsJyro repo (the JoyShockMapper fork it researches); the JSM source is the parent tree (`../`).

## Current focus

**Linux-side input latency and gyro on a fresh Arch install.** See [`8bitdo-ultimate2-arch-linux-troubleshooting.md`](./8bitdo-ultimate2-arch-linux-troubleshooting.md) — root-cause analysis (kernel HID driver claiming the device before Steam can hidraw it), connection-mode capability matrix, and a step-by-step udev-rule fix.

## Long-term direction

Captured in the parent tree's design spec, [`../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md`](../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md): a comprehensive design for an agent-first lab that compares **real Steam Input** vs **real JSM** behaviorally (mapper lanes, agent roles, validation policy, artifact contracts, phase gates). It is the canonical articulation of the long-term direction — cite its line anchors rather than re-deriving the concepts. The owned, executable reformulation of it lives here in [`mapper-conversion-lab-plan.md`](./mapper-conversion-lab-plan.md).

That direction is **preserved (in the parent spec), not active.** Current effort is the Linux-side troubleshooting above.

## Layout

```
jangsjyro/gamepad/         (this lab — a research subdir of the JoyShockMapper fork)
├── README.md                                          (this file)
├── CLAUDE.md                                          (agent conventions)
├── mapper-conversion-lab-plan.md                      (active working plan — Steam-Input⇄JSM converter lab)
├── 8bitdo-ultimate2-arch-linux-troubleshooting.md     (current focus — living doc)
├── vdf/                                               (preserved-active: VDF→JSM tooling + translation knowledge for reuse)
│   ├── README.md
│   ├── vdf_clean.py
│   ├── test_vdf_clean.py
│   ├── translation_audit.md
│   └── reference/   (source-of-truth tuned VDFs)
├── findings/                                          (durable knowledge)
│   ├── gyro_hid.md
│   ├── jsm_linux_port.md
│   └── steam_input_linux.md
├── reference/                                         (raw user-supplied artifacts)
│   └── 8bitdo_dinput_usbTree.txt
├── runs/                                              (per-run evidence — crash backtraces, smoke + steam-input results)
└── tools/                                             (Linux HID/SDL + XI2 diagnostics)
    ├── README.md
    ├── evdev_capture.py
    ├── gyro_enum.py
    ├── gyro_meter.py
    ├── gyro_probe_hid.py
    └── xi2_capture.py

# Long-term-direction design spec lives in the parent tree:
#   ../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md
```

## Hardware reference (durable)

- **Controller:** 8BitDo Ultimate 2 Wireless
- **VID / PID:** `0x2DC8 / 0x6012` (2.4 GHz dongle, D-Input mode)
- Other PIDs in use: `0x310B` (USB wired), `0x6013` (dongle alone). Bluetooth disables gyro and caps polling at 125 Hz.
- **D-Input activation:** hold **Home + B** on power-on (X-Input is the default and exposes neither gyro nor the extra buttons).
- **Firmware floor:** v1.03+ for the 34-byte sensor-bearing HID report (`findings/gyro_hid.md`).

## Surviving tools

Five Linux-friendly diagnostics — see [`tools/README.md`](./tools/README.md). Three are HID/SDL hardware probes useful for verifying the kernel-driver-conflict hypothesis from the troubleshooting doc (`gyro_enum.py` to confirm SDL sees the gyro sensor, `gyro_probe_hid.py` to confirm the hidraw path is reachable, `gyro_meter.py` for a live IMU monitor); two are mapper-output observers (`evdev_capture.py` for the JSM lane at evdev, `xi2_capture.py` for the Steam-Input lane at the XI2/Wayland seat).
