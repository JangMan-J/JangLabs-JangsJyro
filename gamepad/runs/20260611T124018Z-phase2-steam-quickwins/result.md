# Phase 2 — Steam-lane (reference) quick-wins — 2026-06-11

**Status: COMPLETE.** All seven Phase-2 mechanics + a per-binding hold-time probe captured on
real Steam Input (publicbeta, client 1781139754, Wayland/KDE), same synthetic pad + traces as
the JSM lane (`runs/20260602T145517Z-phase2-jsm-quickwins`). Observer: `xi2_capture.py` (XI2
plane); `evdev_capture.py` as negative control (no Steam output at evdev in any slice — holds
throughout). Pipeline: pad holder (`--control-fifo`) → trace replayed into FIFO → Desktop-layout
bindings (autosave vdf `…/413080/controller_xbox360.vdf`, rev 38).

## Per-mechanic verdicts (Steam side of each A-B pair)

| Mechanic | Stimulus → Steam output | vs JSM-lane verdict |
|---|---|---|
| digital (South→F9) | 3 presses → 3 exact F9 pairs | match (JSM exact) |
| tap/hold (East: F10 / Long F11 @450 ms) | 80 ms → F10 on release; 450 ms → **F11 only, F10 suppressed** | same model as JSM tap/hold |
| double press (North: F12 / Double F7 @190 ms window) | lone → F12; pair (90 ms gap) → **F7 only — base NOT fired on first press** | **DELTA: JSM fires base on the pair's first press, Steam suppresses it** |
| chord (West F6; Select+West→F8) | West alone → F6; chord → F8, no Select leak | match (JSM chord override) |
| simultaneous (TL→Shift, TR→E, TL+TR chord→Q) | chord → **Shift held + Q (member's binding LEAKS)**, E suppressed; lone TL after chord → Shift (clean) | **DELTA both ways: Steam leaks the chord member's regular binding (JSM SIMPRESS suppresses both); Steam has NO sticky-state (JSM's lone-press-after-chord bug absent)** |
| trigger soft/full (edge F3 / click F4) | staged pull: F3 down → F4 added → both released (soft held under full) | match (JSM NO_SKIP) — but see anomaly: an instant 0→255 jump in the button-matrix probe emitted **F4 only, no F3** (ramp-dependent soft-pull; JSM's axis-threshold model fires soft regardless) |
| stick→WASD (dpad mode, requires_click 0) | LY− → w pair; LX− → a pair | match |
| per-binding hold time (Start: F5 / Long F2 @**603 ms** custom) | 180 & 480 ms → F5 each (under threshold); 800 ms → **F2 only** | **confirms X.2 from the Steam side: per-binding long-press times are real; JSM has only global HOLD_PRESS_TIME → bounded loss in Steam→JSM** |

## GUI parameters in force (user screenshots, 2026-06-11 07:10–07:12 local)

- Long Press Settings (East): Long Press Time **450 ms**, Turbo off, Fire Start/End Delay 0, Toggle off.
- Double Press Settings (North): Double Tap Time **190 ms**, Turbo off, Fire delays 0, Cycle/Toggle off.
- Button Chord Settings: Require Any/All = **Any**, **Interruptable = ON**, Turbo off, Fire delays 0.
- Trigger group: `adaptive_threshold 3` (from the autosave vdf).
- Full layout: groups for trigger/diamond/joystick-dpad/switches, single Default preset, no action layers
  (`413080/controller_xbox360.vdf` rev 38; Steam stores F11/F12 fine — note xinput prints them as legacy
  keysyms **L1/L2**; the normalizer must fold those).

## Anomaly — transient total emission silence (first pass, preserved in `firstpass-dead/`)

First run of slices 2–9 (06:27–06:31 local, ~1 min after the autosave): F9/F10 emitted (F10's
release stuck ~9 s), everything else **silent** — stimuli confirmed at evdev, layout verified
saved and active. Minutes later the identical slices all passed with no intervention. Trigger
unconfirmed; candidates: the layout/preview GUI screen open during the runs (settings *dialogs*
open do NOT suppress — F9 retest passed with them up), or post-autosave config-activation lag.
**Lab rule going forward: run the `digital` slice as a canary before any Steam-lane session;
if silent, wait/close the config UI and re-run before concluding anything.**
(The spike's "delayed final KeyRelease" was likely this same state forming.)

## Notes

- User keyboard/touchpad activity contaminates captures (physical typing landed in several
  windows; re-runs isolated it). Letter-output bindings are the sensitive ones — F-keys proved
  robust. Slices here were re-run until clean or disambiguated.
- Binding persistence: the Desktop-layout bindings survive synthetic-pad destruction/re-creation
  (proven twice today) — one GUI sitting amortizes over all future sessions.
- Latency analysis not done here; the `.jsonl` artifacts carry timestamps for Phase-3 schema work.
