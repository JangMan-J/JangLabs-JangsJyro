# Phase 2 — JSM-lane behavioral tracer slices (vdf quick-wins, candidate half)

**Date:** 2026-06-02 · **Host:** CachyOS/Wayland/KDE/NVIDIA · **JSM:** this repo `branch-a-port` `68dcb97`, Linux/clang `build-linux/`.

## Method
Each slice = a JSM config (`configs/<slice>.cfg`) + a synthetic stimulus trace (`traces/<slice>.trace`) replayed on the synthetic Xbox-360 uinput pad (`tools/synthetic_gamepad.py --trace`), JSM's keyboard/mouse output grab-captured at evdev (`tools/evdev_capture.py --grab-name JoyShockMapper`). Serial, run-and-observe; one live JSM per slice. Driver: `run-slice.sh`. **No physical pad, no Steam** — this is the JSM (candidate) lane only; the Steam (reference) half is blocked on the Steam GUI (Phase 0b: Steam output is at XI2/seat, not evdev).

This characterizes JSM's **actual** behavior for four `vdf` quick-win mechanics (`vdf/translation_audit.md`). The audit's grades are *static predictions*; these traces are the real-runtime verdicts.

## Results
| Slice | JSM config | Stimulus | JSM output @ evdev | Verdict |
|---|---|---|---|---|
| **taphold** | `E = A B` | EAST 80 ms; EAST 450 ms | tap→`KEY_A` (44 ms); hold→`KEY_B` (~300 ms, fires at 150 ms held) | **exact** — confirms audit quick-win "Face buttons Full_Press+Long_Press → JSM tap `'` / hold `_`". 150 ms `HOLD_PRESS_TIME` boundary verified. |
| **trigfull** | `ZR_MODE=NO_SKIP`, `ZR=RMOUSE`, `ZRF=LSHIFT` | RZ 100; RZ 255; RZ 0 | soft→`BTN_RIGHT`; full→ +`KEY_LEFTSHIFT` (both held, NO_SKIP); release→both up | **exact** — confirms audit quick-win "Trigger fire/ADS LT/RT". Soft/full split correct. ZR fires off the **analog** `ABS_RZ` threshold (matches Phase 0a/1). |
| **stickwasd** | `LEFT_STICK_MODE=NO_MOUSE`, `LUP/LDOWN/LLEFT/LRIGHT=W/S/A/D` | LY −32000; LX −32000 | up→`KEY_W`; left→`KEY_A` (each held while tilted) | **exact** — confirms audit quick-win "Sticks-to-WASD via NO_MOUSE + L{UP,DOWN,LEFT,RIGHT}". |
| **simpress** | `L=LSHIFT`, `R=E`, `L+R=Q` | L+R together; then L alone | L+R→`KEY_Q` ✓; **lone L→`KEY_Q` (WRONG; expected `KEY_LEFTSHIFT`)** | **degraded / bug** — see below. Refutes the audit's clean-quick-win expectation for *repeated* use. |

## Finding: simultaneous-press sticky state (real-runtime, reproducible)
Disambiguated with `simpress2` (lone press **first**): lone L → `KEY_LEFTSHIFT` (correct) → L+R → `Q` (correct) → lone L again → **`Q` (wrong)**. So a lone L press is mapped correctly **until** L has participated in an `L+R` simultaneous press; **afterward the next lone L press re-emits the simultaneous binding `Q` instead of `L`'s own binding** — the sim-press association is not cleared when the chord releases. The first lone press in a fresh session is always correct, so this is **residual state**, not a mapping error.
- **Lab consequence:** the audit lists Simultaneous Press as a clean quick-win; real-runtime evidence says it is clean **once**, then sticky. For the converter this is a `degraded_approximation` for any layout that reuses a sim-press member as a lone button (common). Classify by trace, not by the audit's static grade.
- **Non-semantic boundary:** this is a *behavioral observation*, not a JSM patch — per plan §2, "green = honest classification" here, not "patch JSM so the trace matches." A source root-cause (DigitalButton/Mapping sim-press state) is a follow-up hypothesis, not done here.

## Minor anomaly: disconnect-time spurious trigger press (trigfull only)
~4.4 s after release, coinciding with synthetic-pad **destruction**, JSM emitted a lone `BTN_RIGHT` **down** (no matching up in-window). Not seen in the digital/stick slices. Hypothesis: JSM re-reads the trigger axis during SDL device-removal teardown. Minor; the converter's normalizer should ignore output bracketing a disconnect event.

## Status
Phase 2 JSM-lane half: **3/4 quick-win mechanics confirmed `exact`, 1 (`simpress`) reclassified `degraded` by evidence.** Seeds `kb/canonical/mapper-functions.jsm.json` (plan §9) with real verdicts. The cross-runtime **delta** (vs real Steam Input) for each remains blocked on the Steam-lane spike (needs the user + Steam GUI). Gyro quick-wins (primary gyro mode, deadzone, ratchet) need the `uhid` spoof (Phase 6) — not attempted here.
