# JSM-lane behavior — real-runtime verdicts (synthetic uinput → JSM → evdev)

Durable behavioral facts for the **JSM (candidate) lane** of the mapper-conversion lab,
established by synthetic tracer slices on this box (no physical pad, no Steam). These are
**real-runtime verdicts** that confirm or *refute* the static predictions in
`vdf/translation_audit.md`. Companion to `jsm_linux_port.md` (build/runtime) and
`steam_input_linux.md` (the Steam lane). Pipeline: `tools/synthetic_gamepad.py` →
JSM (`build-linux/`) → `tools/evdev_capture.py --grab-name JoyShockMapper`.

## Verified `exact` (audit quick-wins confirmed) — 2026-06-02
- **Digital button → key**: synthetic `BTN_SOUTH` → JSM `S` → `KEY_SPACE` at evdev, **~2 ms**, exact count+order. (Phase 1, run `20260602T144140Z-phase1-jsm-synthetic-spike`.)
- **Tap vs hold** (`E = A B`): short press (<150 ms) → tap binding `KEY_A` (brief, fires on release); long press (>150 ms) → hold binding `KEY_B` (fires at the 150 ms `HOLD_PRESS_TIME`, holds until release). The documented tap(`'`)/hold(`_`) model and 150 ms boundary hold on synthetic input.
- **Analog trigger soft/full split** (`ZR_MODE=NO_SKIP`, `ZR=RMOUSE`, `ZRF=LSHIFT`): soft pull → `BTN_RIGHT`; full pull (RZ=255) → adds `KEY_LEFTSHIFT` while keeping `BTN_RIGHT` (NO_SKIP); release drops both. **`ZR` fires off the analog `ABS_RZ` axis threshold, not a digital trigger latch** (consistent across Phase 0a real-pad, Phase 1, Phase 2). The reference signal for trigger traces is the analog axis crossing JSM's threshold.
- **Stick → digital direction** (`LEFT_STICK_MODE=NO_MOUSE`, `LUP/LDOWN/LLEFT/LRIGHT`): stick up (`ABS_Y`−) → `KEY_W`, stick left (`ABS_X`−) → `KEY_A`, held while tilted past the inner deadzone.

(Slices in run `20260602T145517Z-phase2-jsm-quickwins`.)

## Refuted / `degraded` (audit prediction corrected by evidence) — 2026-06-02
- **Simultaneous press has sticky state.** `L=LSHIFT`, `R=E`, `L+R=Q`: `L+R` → `Q` is correct, **but a lone `L` press that follows an `L+R` chord re-emits `Q` instead of `LSHIFT`** — the sim-press association is not cleared when the chord releases. A lone `L` press *before* any chord is correct (→`LSHIFT`), so it is residual state, not a mapping error (disambiguated by `simpress2`, lone-press-first). The audit grades Simultaneous Press a clean quick-win; the real-runtime verdict is **clean once, then sticky** → `degraded_approximation` for any layout that reuses a chord member as a lone button. **Likely a genuine JSM bug** (sim-press state machine in `DigitalButton`/`Mapping`); per the lab's non-semantic boundary it is *classified*, not patched. Root-cause in source = open follow-up.

## Minor anomalies
- **Disconnect-time spurious trigger press**: when the synthetic pad is destroyed, JSM emitted a lone `BTN_RIGHT` **down** (trigger axis re-read during SDL device-removal). Seen only in the trigger slice. The normalizer should discard output bracketing a connect/disconnect event.

## Method notes (for reproducing / extending)
- Drive stimuli with a `synthetic_gamepad.py --trace` DSL file; feed the JSM mapping via the command FIFO `/tmp/jsm_command_fifo` (JSM ignores argv on Linux); always `--grab-name JoyShockMapper` so emitted keys/clicks don't leak into the live session.
- `RECONNECT_CONTROLLERS` after the config feed forces JSM to (re)enumerate a pad created after JSM start; a pad created *before* JSM start is also picked up at SDL init.
- Gyro mechanics (primary gyro mode, `GYRO_CUTOFF_SPEED`, ratchet `GYRO_OFF`) are **not** reachable via a plain uinput pad — they need the native-`2dc8:6012` `uhid` spoof so SDL's `SDL_hidapi_8bitdo` surfaces sensors (R2, Phase 6).
- Every verdict above is the **JSM half** of an A-B pair; the **Steam reference half** is blocked on the Steam-lane synthetic spike (needs Steam GUI; observe at XI2 via `tools/xi2_capture.py`).
