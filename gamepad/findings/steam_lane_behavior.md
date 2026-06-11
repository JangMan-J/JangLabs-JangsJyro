# Steam-Input-lane behavior — real-runtime verdicts (synthetic uinput → Steam Input → XI2)

Durable behavioral facts for the **Steam Input (reference) lane**, established 2026-06-11 by
replaying the Phase-2 JSM-lane traces through a real Steam client (publicbeta 1781139754,
Wayland/KDE, Desktop layout on a synthetic Xbox-360 uinput pad). Companion to
`jsm_lane_behavior.md` (the JSM candidate lane) and `steam_input_linux.md` (plane/recognition).
Evidence: `runs/20260611T124018Z-phase2-steam-quickwins/`. These are the **reference halves**
of the Phase-2 A-B pairs — the converter's equivalence rules must reproduce/classify exactly
these deltas.

## Confirmed matches (Steam ≈ JSM model)

- **Digital button → key:** exact press/release pairs.
- **Tap vs hold:** same model both lanes — tap fires on release under the threshold; hold fires
  the long binding *at* the threshold and suppresses the tap binding. Steam's default Long Press
  Time here: **450 ms** (GUI); JSM's default `HOLD_PRESS_TIME`: 150 ms — same semantics,
  different default boundary (comparator must parameterize it).
- **Chorded press:** modifier-held chord overrides the base binding, modifier itself silent —
  matches JSM `L,W=G` semantics (Steam chord settings: Require Any, Interruptable on).
- **Trigger soft/full:** Steam edge(soft)+click(full) under a staged pull ≈ JSM `NO_SKIP`
  (soft stays held while full is active). **Ramp-dependence caveat:** an instant 0→255 axis jump
  emitted full ONLY (no soft) on Steam, while JSM's `ABS_RZ`-threshold model fires soft on any
  crossing — adversarial-trace material for Phase 4.
- **Stick → digital keys (dpad mode):** directional WASD held while past deadzone; matches JSM
  `LEFT_STICK_MODE=NO_MOUSE`.

## Cross-runtime deltas (the converter must classify these)

1. **Double press disambiguation differs.** JSM fires the base binding on the *first* press of a
   double pair, then the double binding; **Steam suppresses the base entirely** when the second
   press lands inside the Double Tap Time (190 ms here). Steam→JSM conversion of a double-press
   binding is `bounded` at best (extra base-keystroke appears); JSM→Steam loses the
   first-press echo.
2. **"Simultaneous press" is not the same primitive.** Steam has no SIMPRESS — only chords owned
   by one button. Consequence: the chord *member's* regular binding **leaks** (TL's Shift was
   held down alongside the chord's Q; the owner's E was suppressed). JSM SIMPRESS suppresses
   both members. Conversion either direction changes member-leak behavior → classify.
3. **JSM's sim-press sticky-state bug has no Steam counterpart.** Lone-press-after-chord emits
   the lone binding correctly on Steam (verified both orders, `simpress`/`simpress2` traces).
   The JSM-side `degraded` classification is JSM-specific, not a Steam semantic.
4. **Per-binding long-press times are real on Steam** (450 ms on one button, custom 603 ms on
   another, both honored in one layout; >603 ms press fired the long binding and suppressed the
   regular). JSM has only global `HOLD_PRESS_TIME` → Steam→JSM is a confirmed bounded loss
   (audit gotcha X.2, now proven from BOTH sides).

## Operational gotchas (Steam lane)

- **xinput keysym aliasing:** F11/F12 print as legacy keysyms **L1/L2** in `xinput test-xi2`
  output — fold them in the normalizer before diffing.
- **Transient emission silence exists.** Once, for ~4 min after an autosave (and possibly while
  the layout GUI screen was up), all bindings except two went silent while stimuli were confirmed
  at evdev; it self-recovered. Settings *dialogs* open do not suppress (retested). **Canary rule:
  run the digital slice first in any Steam-lane session; if silent, don't trust ANY absence.**
- **Captures see the whole seat.** Physical typing/touchpad lands in the same XI2 stream; letter
  outputs (WASD/E/Q) are indistinguishable from typing except by stimulus-timestamp correlation.
  Schedule letter slices in hands-off windows; F-key outputs are robust.
- **Desktop-layout bindings persist across pad re-creation** (no serial on the synthetic pad) —
  one GUI sitting amortizes; only re-verify with the canary.
- Desktop layout lives in the autosave
  `Steam Controller Configs/<acct>/config/413080/controller_xbox360.vdf` — human-readable;
  read it to verify what the GUI actually saved (it caught nothing wrong today, and it is the
  ground truth the converter will eventually consume).
