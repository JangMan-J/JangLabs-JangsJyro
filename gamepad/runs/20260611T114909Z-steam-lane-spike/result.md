# Steam-lane spike — synthetic pad recognition + output plane (2026-06-11)

**Status: PASS — both open questions answered.** The Steam Input (reference) lane is unblocked.

## Questions → answers

1. **Does Steam Input recognize a *synthetic* uinput gamepad?** **YES.** With
   `synthetic_gamepad.py --control-fifo` holding the pad, Steam logged
   `Local Device Found / type: 045e 028e / path: sdl://2 / Product: Xbox 360 Controller`,
   opened it (`Steam controller device opened for index 0`, XInput slot 0) and applied the
   stock SDL mapping. **No `uhid` device is needed for the Steam lane** (uhid remains
   gyro-only, per Phase 1). Evidence: `steam-recognition.txt`.
2. **Is Steam Input's output at the XI2/Wayland seat and NOT at evdev?** **YES — Phase 0b
   generalizes to synthetic input.** 11 injected South presses (`press SOUTH 120` via the
   control FIFO) with A/South bound to **F9** in the Steam Desktop layout produced:
   - **XI2:** 44 events = 11 × (RawKeyPress+KeyPress+RawKeyRelease+KeyRelease), all `F9`,
     device `xwayland-keyboard:10` on the Xwayland seat (`xi2.txt`, `xi2.jsonl`).
   - **evdev:** **0** `KEY_F9`. The only evdev traffic was the stimulus itself —
     22 × `BTN_A` on the synthetic pad (`evdev.txt`, `evdev.jsonl`) — the intended
     negative control.

## Environment

- Steam: native pacman client, **publicbeta** channel, client version **1781139754**;
  launched fresh for this run (was not running).
- Box: CachyOS, Wayland/KDE, kernel 7.1.0-rc7-1-cachyos-rc (per-turn fingerprint).
- `/dev/uinput`: rw via `user:jangmanj:rw-` ACL (node now owner `openlinkhub`, group
  `input` — ACL intact, no impact).
- GUI step (human, one-time): Settings → Controller → enabled Steam Input for the pad,
  bound **A/South → F9** in the Desktop layout.

## Anomalies / notes

- **Stale log path in `steam_lane_spike.sh`:** this client writes
  `~/.local/share/Steam/logs/controller.txt`, not `controller.log`. (Script fixed in this
  commit to try both.)
- **Delayed final KeyRelease:** the 11th pair's `KeyRelease` arrived ~8.4 s after its
  `KeyPress` (all earlier pairs ~120 ms, matching the injected hold). Count and pairing
  are complete; looks like a Steam-side flush/repeat quirk at end of burst. Watch whether
  it recurs in longer slices before modeling timing tolerances for the Steam lane.
- **Open question for re-use:** whether the F9 binding persists for a *re-created*
  synthetic pad (no serial). Re-verify with a quick FIFO press at the start of the next
  Steam-lane session.

## What this unblocks

The reference half of every A-B pair: the seven Phase-2 mechanics can now be re-run
through Steam Input (`xi2_capture.py` as observer) to produce the first cross-runtime
deltas, then the Phase-4 adversarial gotchas. Converter (Phase 9) remains gated on those
trace-verified rules.
