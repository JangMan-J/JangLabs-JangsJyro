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

## Official semantics (Steamworks docs — naming/mechanism for the verified behavior)

Steam Input partner docs (`https://partner.steamgames.com/doc/features/steam_controller`,
sub-page `…/activators`, read 2026-06-11; **local snapshots:
`reference/steamworks-input-docs/`**) confirm and *mechanize* the runtime verdicts:

- The base-binding suppression we measured on long press, double press, and the 603 ms probe is
  the documented **`Interruptable`** mechanism: *"Any interruptable activators on the same button
  will not fire if a long/double press is fired."* **Converter implication: `interruptable` is a
  per-activator vdf parameter, default on.** With it OFF, Regular fires alongside Long/Double —
  which maps to a *different* JSM construct than the tap/hold pair (JSM tap/hold ≈ interruptable
  ON). The converter must read this flag, not assume the default.
- **Two more press primitives exist beyond the Phase-2 set:** `Start_Press` (fires on press-down,
  instantly deactivates even if held) and `Release_Press` (fires on release). Future mechanics
  rows for the capability matrix; JSM analogues (instant `!`-style vs release bindings) need
  their own A-B traces before any equivalence rule.
- Chorded press is documented only as "a specific button must be held down at the same time" —
  the docs make **no claim that the chord member's own bindings are suppressed**, consistent with
  the member-leak we measured (and confirming the leak is by-design, not a bug to be waited out).
- Fire Start/End Delay range is 0.0–1.0 s; Turbo/Toggle/Cycle exist per-activator. All were 0/off
  in this run's layout (screenshots + vdf) — variations are Phase-4+ material.
- Doc map for later phases (same docs root): *Action Set Layers* (Phase-4 `remove_layer` gotcha),
  *Mode Shifting*, *In-Game Actions File* / *Action Manifest* (the non-legacy config world), and
  *Legacy Mode Bindings* — the desktop-layout vdf we parse IS legacy mode; the audit's rows
  should eventually be cross-checked against both worlds.

Per the lab spine these doc statements are *naming and mechanism* for behavior already verified
by trace — any NEW claim sourced here (Start/Release press, interruptable-off, delays) stays a
hypothesis until a trace fires it.

## Boundary semantics (Chunk C2, 2026-06-11 — runs `20260611T151747Z-chunk-c2-steam-boundary`)

- **Long Press Time is inclusive and tick-exact at the configured value:** 430ms → tap (F10);
  450ms and 470ms → hold (F11) at Long Press Time 450. Contrast JSM: exclusive + poll slack
  (`jsm_lane_behavior.md` boundary section) — comparator must parameterize per lane.
- **Double Tap Time is DOWN-to-DOWN referenced, exclusive at the configured value:** 170ms d2d
  fires the double; 190ms d2d (≈130ms release-to-down) does NOT — which rules out
  release-referencing by construction. JSM's window is release-to-down ⇒ epoch mismatch,
  `bounded_approximation` for window translation.
- **`interruptable 0` (vdf, on Full_Press) CONFIRMED at runtime** — Regular fires on
  press-down and is NOT suppressed when Long fires at threshold; both keys active together.
  Upgrades the docs-sourced hypothesis to verified. (First attempt edited the Long_Press
  activator's settings — no behavioral change; the flag belongs on the activator being
  *interrupted*, i.e. Full_Press.) Converter: `interruptable` is load-bearing for tap/hold
  translation and must be read per-activator, never assumed default.
- **OPEN — trigger soft-pull did not fire in C2** (staged 0→100→255 NOR instant), contradicting
  the Phase-2 staged result. Suspect `adaptive_threshold 3` state or intermediate value too low.
  Follow-up queued (replay the exact Phase-2 staged trace on a fresh client + a RZ=200 staged
  variant). The Phase-2 trigger entry above stands UNCHANGED until adjudicated.

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
- **Programmatic binding control WORKS (verified 2026-06-11, F9→F7 probe):** edit the autosave
  vdf on disk, then **restart Steam** — the edited bindings are live (8/8 presses emitted the
  edited key). On-disk edits are NOT picked up while Steam runs (in-memory copy wins), and
  shutdown does NOT write back over your edit. Protocol: backup → edit → `steam -shutdown` →
  relaunch (nested env: `tools/steam-virtual-env.sh`) → canary slice → run. Never disk-edit and
  GUI-edit the same layout concurrently. **This removes the GUI sitting for any mechanic whose
  vdf encoding we know** (activator types/settings per the docs snapshots + this layout as the
  template). Phase-2 reference layout archived at `reference/desktop-layout-phase2-reference.vdf`.
