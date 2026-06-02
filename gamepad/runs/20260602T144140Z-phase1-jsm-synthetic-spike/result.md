# Phase 1 tracer bullet — synthetic uinput gamepad → JSM → evdev (JSM lane): **PASS**

**Date:** 2026-06-02 · **Host:** CachyOS (Arch), Wayland + KDE, NVIDIA · **JSM:** this repo (JangsJyro fork) `branch-a-port` HEAD `8d100f1`, built Linux/clang.

## Question (plan §10 Phase 1, §11; the deferred crux)
Both Phase 0 runs drove the lanes with the **real** 8BitDo pad. Phase 1 needs **synthetic** injection — unproven on either lane. This run answers the cheapest half: **does a synthetic virtual gamepad drive JSM → keyboard/mouse output observable at evdev, with no physical controller?**

## Method
- Built JSM on Linux from source: `cmake -S . -B build-linux -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++` (SDL3 `release-3.4.8` via CPM; ~1.5 min; 48 warnings, 0 errors). Binary starts + SIGTERM-stops clean (exit 0, no `terminate`, no core) — the branch-a-port crash fixes hold.
- Synthetic pad: `tools/synthetic_gamepad.py` creates a **plain uinput Xbox-360-layout device** (`vendor 0x045e product 0x028e`, "Microsoft X-Box 360 pad", standard `BTN_*` + `ABS_X/Y/RX/RY/Z/RZ/HAT0`). **No `uhid` / native-HID spoof.**
- Config via the command FIFO `/tmp/jsm_command_fifo`: `RESET_MAPPINGS` / `S = SPACE` / `ZR = LMOUSE` + `RECONNECT_CONTROLLERS`.
- Output observed with `tools/evdev_capture.py capture --name JoyShockMapper --grab-name JoyShockMapper` (grabbed → emitted SPACE/clicks did **not** leak to the live KDE session).
- Orchestration: `orchestrate.sh` (this dir). Stimulus log: `injector.log`; capture: `capture.jsonl` / `capture.txt`; JSM console: `jsm.stdout.log`.

## Result — exact, 1:1, ~2 ms
- **SDL3 classifies the synthetic uinput pad as a gamepad.** JSM: `[AUTOCONNECT] Going from 0 devices to 1` → `1 device connected`. Device list: `event30 [gamepad] 'Microsoft X-Box 360 pad' (045e:028e)`. **A generic uinput gamepad is sufficient for digital buttons + analog triggers — the native-8BitDo `uhid` spoof is only needed for gyro (R2, Phase 6).**
- **`BTN_SOUTH` → `KEY_SPACE`** (JSM cardinal `S`): 2 presses in, 2 `KEY_SPACE` down/up out, exact order. `BTN_SOUTH` down `14:48:01.126` → `KEY_SPACE` 1 at `…681.128` = **~2 ms** translation latency (matches Phase 0a's 1–3 ms real-pad figure).
- **`ABS_RZ` ramp → `BTN_LEFT`** (JSM `ZR`): 2 trigger pulls in, 2 `BTN_LEFT` down/up out. **`ZR` fires off the analog `ABS_RZ` threshold**, not a digital trigger latch — confirms the Phase 0a behavioral finding on synthetic input too. (Reference signal for trigger traces = the analog axis crossing JSM's threshold.)
- Capture totals: 16 events = 2×`KEY_SPACE`↓↑ + 2×`BTN_LEFT`↓↑ (+ SYN). Zero spurious output; pad-disconnect (`Going from 1 devices to 0`) seen cleanly when the injector destroyed the device.

## Consequence for the lab
- **Phase 1 DoD met for the JSM lane**: one synthetic `uinput` trace → JSM → one observable cross-plane output, classified `exact` (`S=SPACE` count+order match, latency recorded). The JSM lane now has a **complete synthetic trace-runner → output-observer pipeline** (`synthetic_gamepad.py` → JSM → `evdev_capture.py`) usable headlessly, no physical pad.
- **Still open (needs the user / GUI):** the **Steam Input lane** synthetic-injection half — does Steam Input recognize a *synthetic* controller, and is its output observable (Phase 0b: Steam output is at the **XI2 / Wayland seat**, not evdev; observe via `tools/xi2_capture.py`). That requires Steam running with Steam Input configured for the synthetic pad — not autonomously completable here.
- **Next autonomous step:** Phase 2 — walk the `vdf` "quick wins" as JSM-lane tracer slices using this pipeline (synthetic stimulus → JSM → evdev), building the comparator/normalizer only as far as each slice needs. The Steam (reference) half of each A-B pair is blocked on the Steam-lane spike above.

## Reproduce
```
ROOT=~/JangLabs/jangsjyro
cmake -S "$ROOT" -B "$ROOT/build-linux" -G Ninja -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ && cmake --build "$ROOT/build-linux" -j
bash "$ROOT/gamepad/runs/20260602T144140Z-phase1-jsm-synthetic-spike/orchestrate.sh"
```
Needs rw on `/dev/uinput` (user is in `input` + has an `user:jangmanj:rw-` ACL; verified). Build dir `build-linux/` is git-ignored.
