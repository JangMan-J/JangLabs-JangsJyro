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
- **Chorded press** (`L=NONE`, `W=B`, `L,W=G`): `W` alone → `KEY_B`; `W` while `L` held → `KEY_G` (the chord overrides the base binding). Distinct from simultaneous press — no sticky-state issue observed.
- **Double press** (`N=B`, `N,N=X`): single → `KEY_B`; two presses within `DBL_PRESS_WINDOW` → `KEY_B` (first) then `KEY_X` (second). Matches the documented "first press fires the base binding, second fires the double" model.
- **Global `HOLD_PRESS_TIME`** (audit gotcha **X.2**): `HOLD_PRESS_TIME=300` governs the tap/hold boundary for **every** binding at once (`E` and `S` both flip tap→hold at 300 ms). JSM has no per-binding hold time, so Steam's per-binding `Long_Press` values translate to a single global → bounded loss. Confirmed, not refuted (the limitation is real and exactly as the audit predicts).

(Slices in run `20260602T145517Z-phase2-jsm-quickwins`.)

## Refuted / `degraded` (audit prediction corrected by evidence) — 2026-06-02
- **Simultaneous press has sticky state.** `L=LSHIFT`, `R=E`, `L+R=Q`: `L+R` → `Q` is correct, **but a lone `L` press that follows an `L+R` chord re-emits `Q` instead of `LSHIFT`** — the sim-press association is not cleared when the chord releases. A lone `L` press *before* any chord is correct (→`LSHIFT`), so it is residual state, not a mapping error (disambiguated by `simpress2`, lone-press-first; a 600–700 ms gap does **not** clear it, so it is persistent residual state, not a short race). The audit grades Simultaneous Press a clean quick-win; the real-runtime verdict is **clean once, then sticky** → `degraded_approximation` for any layout that reuses a chord member as a lone button. Per the lab's non-semantic boundary it is *classified*, not patched.
  - **Root-cause hypothesis (source review — NOT runtime-confirmed, treat as a lead).** `JoyShock::getMatchingSimBtn` (`src/JoyShock.cpp`) decides two buttons are chording with `index != iter->first && button1->getState() == button2->getState()` — pure **state-equality**, not "both specifically in `WaitSim`". The author flagged it inline: *"POTENTIAL FLAW: the mapping you find may not necessarily be the one that got you in a Simultaneous state."* In the `DigitalButton` `pocket_fsm` (`NoPress→WaitSim→SimPressSlave/SimPressMaster→SimRelease→NoPress`), a chord member that has not cleanly settled back to `NoPress` (relative to the partner's poll) can be observed in a state equal to the new presser's `WaitSim`, so `getMatchingSimBtn` re-pairs them and re-enters the sim mapping (`Q`) instead of the lone binding. **Confirm** by `DEBUG_LOG`-ing both buttons' states across the second lone press, or by widening the state-match to require `WaitSim`/checking `_masterPress`. (Real-runtime evidence is authoritative here; this is a source hypothesis only.)

## Minor anomalies
- **Disconnect-time spurious trigger press**: when the synthetic pad is destroyed, JSM emitted a lone `BTN_RIGHT` **down** (trigger axis re-read during SDL device-removal). Seen only in the trigger slice. The normalizer should discard output bracketing a connect/disconnect event.

## Method notes (for reproducing / extending)
- Drive stimuli with a `synthetic_gamepad.py --trace` DSL file; feed the JSM mapping via the command FIFO `/tmp/jsm_command_fifo` (JSM ignores argv on Linux); always `--grab-name JoyShockMapper` so emitted keys/clicks don't leak into the live session.
- **evdev face-button aliasing (synthetic-pad gotcha):** `BTN_NORTH`==`BTN_X` (0x133), `BTN_WEST`==`BTN_Y` (0x134) — the evdev *names* are letter buttons, not screen positions. On an Xbox-360 layout SDL maps `BTN_A`→south, `BTN_B`→east, `BTN_X`→west, `BTN_Y`→north, so a synthetic pad must inject **WEST via `BTN_NORTH` and NORTH via `BTN_WEST`** (SOUTH=`BTN_SOUTH`/A, EAST=`BTN_EAST`/B are fine). `synthetic_gamepad.py`'s button map already encodes this; a slice that gets no output for N/W (but works for S/E) is almost always this swap.
- `RECONNECT_CONTROLLERS` after the config feed forces JSM to (re)enumerate a pad created after JSM start; a pad created *before* JSM start is also picked up at SDL init.
- Gyro mechanics (primary gyro mode, `GYRO_CUTOFF_SPEED`, ratchet `GYRO_OFF`) are **not** reachable via a plain uinput pad — they need the native-`2dc8:6012` `uhid` spoof so SDL's `SDL_hidapi_8bitdo` surfaces sensors (R2, Phase 6).
- Every verdict above is the **JSM half** of an A-B pair; the **Steam reference half** is blocked on the Steam-lane synthetic spike (needs Steam GUI; observe at XI2 via `tools/xi2_capture.py`).
