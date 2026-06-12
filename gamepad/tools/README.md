# Tools — Linux HID/SDL diagnostics

Seven Python tools for the 8BitDo Ultimate 2's input plumbing, observing mapper output, driving a mapper synthetically, and normalizing captures — plus a guided Steam-lane spike harness (`steam_lane_spike.sh`). The HID/SDL probes were originally written during Windows-side investigations but are platform-portable and useful for the current Linux-side input-latency work; the capture/normalize tools, synthetic gamepad, and Steam-lane harness were built for the Linux mapper-conversion lab.

Run from the gamepad subtree root (`gamepad/`).

| Script | Purpose | Linux deps |
|--------|---------|------------|
| `gyro_enum.py` | SDL device enumeration. Lists every joystick SDL sees, whether it's a GameController, and whether it exposes a gyro sensor. **Use first** — confirms whether SDL is even seeing the controller as a sensor-bearing device. | `pysdl2`, `pysdl2-dll` |
| `gyro_probe_hid.py` | Raw-HID byte-change probe. Three phases (idle / sticks / rotate); pinpoints which bytes in the input report carry gyro. Writes `hid_probe_report.txt`. **Use to confirm the hidraw path is reachable** and the 34-byte sensor-bearing report shape matches `findings/gyro_hid.md`. | `hidapi` |
| `gyro_meter.py` | Live IMU angular-velocity monitor — zone strip, virtual-cursor mockup, polling-rate auto-detect. Auto-selects SDL sensor path vs raw HID. Useful as a live-feedback tool when toggling kernel modules / udev rules. | `pysdl2`, `pysdl2-dll`, `hidapi` |
| `evdev_capture.py` | **The mapper-conversion-lab output observer.** `list` enumerates every readable `/dev/input/event*` with a capability tag (keyboard / mouse / gamepad) so you can spot a mapper's virtual output devices (`JoyShockMapper_KEYBOARD`/`_MOUSE`, Steam's `extest fake device`, …); `capture` `select()`s over chosen devices and logs KEY/REL/ABS events with timestamps (`--name`/`--exclude` filter by name, `--grab`/`--grab-name` EVIOCGRAB so synthetic output doesn't leak to the compositor, `--seconds`, `--jsonl`). Compositor-agnostic — the basis for observing mapper output on Wayland. | `python-evdev`, `input` group |
| `xi2_capture.py` | **The Steam-Input-lane observer** (X11/XInput2 counterpart to `evdev_capture.py`). `devices` lists XI2 devices with seat/XTEST flags; `capture` parses `xinput test-xi2 --root` (under `stdbuf -oL`) and logs key/button events with their **source device**, so the X11/XI2 plane is distinguishable from evdev. Needed because **Steam Input on Wayland emits at the compositor seat (XI2-observable), not at evdev** (`findings/steam_input_linux.md`). | `xorg-xinput`; `python-xlib` (optional, keysym names); an X/Xwayland display |
| `synthetic_gamepad.py` | **Synthetic input provider + trace runner** — creates a uinput Xbox-360-layout gamepad (`045e:028e`, "Microsoft X-Box 360 pad") so a mapper can be driven **without the physical pad**. Three modes: built-in demo, `--trace FILE` (DSL: `press/down/up/axis/wait`), and `--control-fifo PATH` (live on-cue injection — write DSL lines, `quit` to stop). SDL classifies it as a gamepad (Phase 1 verified: `BTN_SOUTH`→`KEY_SPACE`, `ABS_RZ`→`BTN_LEFT` at evdev, ~2 ms). evdev face-button alias gotcha is handled (WEST=`BTN_NORTH`/X, NORTH=`BTN_WEST`/Y). The native-8BitDo `uhid` gyro spoof is a separate later escalation. | `python-evdev`, rw `/dev/uinput` |
| `normalize_capture.py` | **Event normalizer** — folds an `evdev_capture.py --jsonl` dump into a mapper-neutral, press-paired event stream (canonical names, durations, timestamps relative to the first event); the form the eventual comparator diffs across lanes. Auto-surfaces anomalies (e.g. still-held-at-end). evdev lane now; XI2 lane is a follow-up. | stdlib only |
| `steam_lane_spike.sh` | **Guided Steam-Input-lane spike harness** (the Steam half of Phase 1). Automates everything except the Steam Input GUI binding: creates a live-controllable synthetic pad, walks you through enabling Steam Input + binding South→F9, then captures **both** planes and reports F9-at-XI2 vs F9-at-evdev (Phase 0b: Steam emits at the XI2/seat, not evdev). Run with Steam up. | the above tools; Steam; `xinput` |
| `steam-virtual-env.sh` | **Seat-free Steam lane** (verified 2026-06-11): nested headless KWin (`--virtual`, own Xwayland) + Steam inside it. Steam Input output lands ONLY on the nested seat — the user keeps their desktop, and user typing cannot contaminate captures. Prints the nested DISPLAY (also in `/tmp/jsmlab_display`); observe with `DISPLAY=<nested> xi2_capture.py`. | `kwin_wayland`, Steam |
| `build-jsm.sh` | **Turnkey Linux build** of the parent JSM fork (the `findings/jsm_linux_port.md` recipe as an executable): clang for both C and C++ (gcc-16 ICEs on SDL3 Wayland C), SDL3 3.4.8 via CPM, into the git-ignored `build-linux/`. | `cmake`, `ninja`, `clang`, SDL build deps |

`test_normalize_capture.py` unit-tests `normalize_capture.py` (stdlib `unittest`, no devices): `python3 -m unittest test_normalize_capture -v`.

| Script | Purpose | Linux deps |
|--------|---------|------------|
| `vdf_layout_gen.py` | **Programmatic VDF layout generator** for Phase-4 diagnostic layouts. Builds layouts via a structured data model (Pairs) and validates every output with a parse→emit→reparse round-trip. Key constraint: **F1–F10 only across all layouts** (F13+ unproven on this XI2 stack; F11/F12 alias to L1/L2 keysyms). Four sub-commands: `marker` (button_y = test button with Start_Press/Release_Press/Full_Press/Double_Press → F1–F4, DTT=190 ms; button_a canary F5; button_b tap/hold F6/F7; button_x interruptable=0 probe F8/F9), `release-press-isolated` (Release_Press discrimination layout: button_a isolated F1, button_b Start+Release F2/F3, button_x Full+Release F4/F5 [suspected blocker], button_y Double+Release F6/F7 DTT=190), `remove-layer` (F1 canary, F2 base, F3 layer override; binding strings `controller_action add_layer 1 1 0` / `remove_layer 1 1 0` — EMPIRICALLY VERIFIED format from 130+ real configs; action_layers block with set_layer=1 generated), `action-set-swap` (F1/F2 in Default id=0, F3/F4 in SetB id=1; `controller_action change_preset <id> 1 0` — UNVERIFIED-HIGH-RISK hypothesis, no corpus evidence; L3 not on critical-path traces). Every layout factory enforces key-uniqueness as a generator invariant (`assert_all_keys_unique` raises on collision). Source of truth for `reference/phase4-layouts/*.vdf` — never hand-edit those files without regenerating via this tool. | stdlib only |

`test_vdf_layout_gen.py` unit-tests `vdf_layout_gen.py` (75 tests, stdlib only): `python3 -m unittest test_vdf_layout_gen -v`.

`test_phase4_traces.py` validates all trace DSL files in `tools/phase4/` for syntax, structure, and verdict-check documentation (16 tests, stdlib only): `python3 -m unittest test_phase4_traces -v`.

## Phase-4 trace scripts (`tools/phase4/`)

Replay these with `synthetic_gamepad.py --trace <file>` against the matching layout (see `reference/phase4-layouts/README.md`). Each file has a `# VERDICT CHECK` comment header stating the Oracle-model prediction being pinned and what comparator output to expect.

Layout `marker_layout.vdf` — button_y (THE test button): Start_Press→F1 (at DOWN, in-stream marker), Release_Press→F2 (at UP, in-stream marker), Full_Press→F3 (Regular, delayed to first-down+DTT=190 ms), Double_Press→F4 (at second-down). DTT=190 ms, `interruptable` default. button_a canary F5; button_b tap/hold F6/F7; button_x interruptable=0 probe F8/F9.

| Script | Layout | Lane | Oracle pin |
|--------|--------|------|-----------|
| `phase4/vary_hold_d2d_pin.txt` | `marker_layout.vdf` | Steam | Pin #1: F3 (Regular) emission at first-down + DTT=190 ms regardless of hold duration (6 batches); F1/F2 timing side-channel |
| `phase4/singles_anchor_set.txt` | `marker_layout.vdf` | Steam | Pin #1 extended: N=8 varied holds for poll-slack distribution; F1 (Start) + F2 (Release) samples included |
| `phase4/double_emission_timing.txt` | `marker_layout.vdf` | Steam | Pin #2: F4 (Double) fires at second-down ~immediately (6 double probes d2d=60–185 ms; 2 boundary singles at 190/220 ms) |
| `phase4/held_double_watch.txt` | `marker_layout.vdf` | Steam | Pin #3: held-double output shape — watch for spurious F4 at first-down + DTT boundary (retracted re-send clause); 3 probes |
| `phase4/rz200_staged_trigger.txt` | `desktop-layout-phase2-reference.vdf` | **Both** | Staged vs instant trigger ramp at RZ=200; reproduces Steam-vs-JSM instant-jump delta (batch D); verify soft+full on staged path both lanes |

## Linux-specific notes

- The kernel's `hid-generic` / `xpad` driver may claim the device before user-space code can open `/dev/hidraw*` — see `../8bitdo-ultimate2-arch-linux-troubleshooting.md`. If `gyro_probe_hid.py` returns "Permission denied" or no device, the udev rule from that doc is likely missing.
- Run as your normal user once udev grants `MODE="0666"` for the relevant VID/PID. `sudo` is not required.
- Wayland and X11 sessions both work for these scripts (none of them grab keyboard/mouse input).

## Install

The minimum for `gyro_probe_hid.py` alone:

```sh
pip install hidapi
```

For SDL-based scripts:

```sh
pip install pysdl2 pysdl2-dll
```

System SDL3 packages are not required — `pysdl2-dll` ships its own. Confirm SDL availability with `gyro_enum.py` before reaching for `gyro_meter.py`.
