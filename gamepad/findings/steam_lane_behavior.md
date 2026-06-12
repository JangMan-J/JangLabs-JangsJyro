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
   first-press echo. **Mechanism (docs, user-confirmed): interruptable activators on the button
   are *paused* until the double-press time passes** — measured: an outside-window single's
   F12 emitted at first-down + ~window + 35 ms (C2 probe 2). So the delta is count AND latency:
   every Steam single on a double-bound button is delayed by up to the Double Tap Time, while
   JSM's base fires immediately. Decision epoch and emission timing RESOLVED (oracle-attested
   2026-06-11, trace-consistent): the window is **down-to-down** from the first down; the double
   fires **immediately on the second down**; the suppressed single fires at **first-down + DTT
   exactly**. Full model + remaining verification pins: §*Oracle model* below.
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
- **Double Tap Time: epoch is DOWN-TO-DOWN** (oracle-attested 2026-06-11; supersedes the
  d2d-vs-r2r ambiguity). C2 traces consistent: release-to-DOWN ruled out by measurement (190ms
  d2d ≈ 130ms r2d fired single); 170ms d2d fires double; 190ms d2d at DTT=190 fired single —
  matching the oracle's **strictly-before-DTT** bound. The queued vary-the-hold discriminating
  probe is downgraded to a cheap Phase-4 verification trace (pin, don't discover). The epoch
  differs from JSM's proven release-to-down ⇒ `bounded_approximation` for window translation.
- **`interruptable 0` (vdf, on Full_Press) CONFIRMED at runtime** — Regular fires on
  press-down and is NOT suppressed when Long fires at threshold; both keys active together.
  Upgrades the docs-sourced hypothesis to verified. (First attempt edited the Long_Press
  activator's settings — no behavioral change; the flag belongs on the activator being
  *interrupted*, i.e. Full_Press.) Converter: `interruptable` is load-bearing for tap/hold
  translation and must be read per-activator, never assumed default.
- **Trigger soft-pull threshold is ADAPTIVE STATE, not a constant** (adjudicated
  `runs/20260611T153109Z-trigger-softpull-adjudication`): on a fresh client, staged RZ=100
  does NOT fire the soft binding (F4 only) — yet the *identical* stimulus verifiably fired
  F3 in Phase 2 (capture on record), after a session of heavy trigger use. Staged RZ=200
  fires soft+full reliably. One crossing does not recalibrate within-session. Hypothesis
  (unproven): `adaptive_threshold 3` migrates the soft threshold with usage. Consequences:
  (1) the Phase-2 staged trigfull entry above is REAL but NOT reproducible from cold —
  treat the soft threshold value as unstable across sessions; (2) the structural delta
  stands confirmed on consistent evidence: Steam instant 0→255 fires full-only, JSM fires
  soft+full — NOT an artifact; (3) Phase-4 adversarial traces use RZ=200 for staged soft
  pulls; (4) converter: Steam soft-pull translations inherit threshold instability —
  classify trigger soft-pull mappings no better than `bounded_approximation`, with the
  adaptive-threshold caveat named in the loss.

## Oracle model — down-anchored activator timing (user-attested 2026-06-11, session 6)

The user (deep Steam Input mechanics oracle, memory `user-steam-input-mechanics-expert`)
resolved the open double-press questions and supplied the underlying timing axiom. Claim
strength: **oracle-attested** — highest-prior hypothesis class in this lab; the ★ claims are
already trace-corroborated, the rest get pinned by Phase-4 verification traces before KB
seeding (anti-Goodhart D3: the KB seeds only from trace-verified rules).

**The axiom:** Steam Input rarely, if ever, applies timers to key-UP events when calculating
activators. Activator timers anchor to DOWN-event timestamps. (Release Press is up-*triggered*
by definition; the axiom is about where *timers* anchor.)
**RETRACTED (user, same day, after app-plane logger testing):** the original axiom's second
clause — "while held, the action is re-sent continuously at some interval" — was an
application-layer artifact of the user's earlier personal testing: the bound action's *state* is
simply held. App-plane observation (keystroke logger, 2026-06-11): a held Steam binding is one
key-down → held state → key-up at release; no re-send chatter, no inherent repeat. (Game/OS-side
autorepeat of a held key is a separate downstream phenomenon.) Down-anchored *timers* stand.
Caveat on the user's prior personal observations generally: they captured their OWN (HID) input,
not Steam/JSM's secondary output — claims about output-plane behavior from that testing carry
lower weight than claims about activator decision logic.

**Worked double-press semantics** (Regular = 'a', Double = 'b', DTT = 250 ms, Regular has the
default interruptible flag):

| Stimulus | Behavior (oracle) |
|----------|-------------------|
| Quick single press (released < DTT) | 'a' fires at **first-down + DTT exactly** — not before, not at release ★ |
| Single press, held | 'a' goes down at first-down + DTT, then is **held as state** until release (re-send clause retracted) |
| Second down strictly before first-down + DTT | 'b' fires **immediately on the second down** ★ (epoch d2d) |
| Second press held | 'b' down at the second down; held as state until release. The original "repeat-firing from first-down + DTT" claim is retracted with the pump — whether ANY output transition occurs at first-down + DTT is now a Phase-4 trace target |
| Any time after 'a' has fired | 'b' can no longer fire (window closed; interruptible default) |

★ trace corroboration: C2 probe 2 measured the suppressed single at first-down + window + ~35 ms
(≈ DTT + transport/poll slack); C2 epoch probes (170 ms d2d → double; 190 ms d2d at DTT=190 →
single) match down-to-down with a strictly-before bound; release-to-down was already ruled out
by measurement.

**New sharp predictions for Phase-4 pinning** (each cheap; each becomes a KB rule when it fires):

1. Singles emission anchored at first-down + DTT regardless of hold/release time (vary the hold).
2. Double emission at second-down with ~zero added latency (emission-timing trace).
3. Held-double output shape: 'b' down at second down, held until release — and specifically
   whether anything at all happens at first-down + DTT (the retracted repeat-onset claim makes
   this the interesting boundary to watch).
4. ~~Held-single re-send interval~~ **RESOLVED at the app plane (user's logger test,
   2026-06-11): held binding = one held key, no re-send chatter.** XI2/evdev confirmation rides
   along free in any Phase-4 capture (Phase-2/C2 Turbo-off captures already agree).

**Converter implications:** singles on double-bound buttons inherit a fixed +DTT latency on
Steam (JSM fires the base immediately — count AND latency delta, classified above); window
translation JSM↔Steam stays `bounded_approximation` (release-to-down vs down-to-down epochs);
held-output equivalence is plain key-state hold on both lanes (no Steam-side repeat pump to
model — Turbo, when enabled, is its own explicit activator setting, not a default behavior).

## XI2 observation-plane delivery model (batch 1b, 2026-06-12 — runner-verified, lead-gated)

Probes P1–P4 (`runs/20260612T053331Z-phase4-pin-batch1/`) resolved the apparent "stuck key" and
"deferred release" anomalies into a delivery model:

- **Steam Input emits at the XI2 RAW layer; raw timestamps are authoritative.** Raw press/release
  pairs land at the true emission moments (pipeline latency ~34 ms from stimulus, consistent
  across all probes and matching C2's ~35 ms).
- **Key-layer (device) events are flush-on-next-raw-event queue artifacts.** Each key-layer event
  is delivered only when the NEXT raw event arrives; the final pending release has no successor
  and is synthesized by `xinput test-xi2` itself at client exit (P4: a second overlapping capture
  sees nothing when the first dies). Server key state stays UP throughout (P3: `xinput
  query-state` all-up during a "stuck" window).
- **RULE: all timing analysis and comparator input MUST use Raw* events only.** Key-layer
  timestamps (and hold-durations derived from them) are delivery noise. Presence-based prior
  verdicts are unaffected; an audit of `normalize_capture.py` event-class precedence is queued to
  confirm no committed verdict ever keyed on key-layer release timing.
- **Suppressed-single output shape (oracle model confirmed at raw layer):** quick tap (release
  < DTT) → the Regular key fires at first-down+DTT as a **~34 ms raw tap** (duration plausibly
  `controller_min_activation_time` = 0.0333 s — INFERRED association, unpinned); held past DTT →
  Regular fires at first-down+DTT and the raw key **mirrors the button state** (release at
  physical up). Oracle prediction 1 confirmed at 120 ms AND 400 ms holds.
- **Release_Press does not emit at all on the four-activator marker button** — absent at the raw
  layer with the double-window open (release at 120 ms) AND closed (release at 400 ms);
  suppressed-while-window-open is FALSIFIED. **Oracle rule (user-attested 2026-06-12): Release
  Press is almost never suppressed as long as it is associated with what Steam perceives as an
  actual PHYSICAL input (vs an additional command from another input).** The marker button's
  press is the same physical press that fired Start_Press, and all interruptible flags were
  default ⇒ under the oracle rule F2 should have fired ⇒ hypothesis weight shifts to **our vdf
  encoding/structure** (the token spelling `Release_Press` is unverified against any
  Valve-written file: the only on-box instance is our own generated layout, and Steam never
  rewrites the autosave, so no serializer ground truth exists). Isolated-variant discrimination
  queued; under the oracle rule it predicts isolated-Release_Press FIRES if our encoding is
  right, and stays silent if the encoding is the fault.
  **Oracle mechanic (user-attested 2026-06-12): Release_Press has the shortest command emit time
  of all activators — it fires a single COMBINED down/up at the same instant, because unlike most
  activators it is not queued to any button state, merely edge-FIRED by one.** Observational
  consequences: (a) the expected signature is a **zero/near-zero-duration raw pair** at
  physical-release + pipeline; (b) the capture → normalizer path must pair identical-timestamp
  raw events (dur_ms ≈ 0) without classing them as noise or unmatched — UNTESTED for this case,
  verification queued before the discrimination pass; (c) a zero-width pulse is also the best
  possible release-side timestamp marker — better than a held key — if it emits at all.

## Operational gotchas (Steam lane)

- **xinput keysym aliasing:** F11/F12 print as legacy keysyms **L1/L2** in `xinput test-xi2`
  output — fold them in the normalizer before diffing.
- **Transient emission silence exists.** Once, for ~4 min after an autosave (and possibly while
  the layout GUI screen was up), all bindings except two went silent while stimuli were confirmed
  at evdev; it self-recovered. Settings *dialogs* open do not suppress (retested). **Canary rule:
  run the digital slice first in any Steam-lane session; if silent, don't trust ANY absence.**
- **Stimulus-confirmation discipline (2026-06-12, the BTN_SOUTH session).** The
  `synthetic_gamepad.py` control-FIFO DSL takes SHORT button names (`press SOUTH`);
  `press BTN_SOUTH` logs `WARN bad action` in the holder log and injects NOTHING. An entire
  session of "silent canary" was stimulus-never-injected, misread first as transient silence and
  then as SI-disabled. **Amended canary rule: on ANY output silence, FIRST check the holder log
  for WARN lines / confirm the stimulus at evdev — only a confirmed-injected, output-silent
  canary says anything about the Steam lane.** (The historical ~4-min transient-silence
  observation above had evdev-confirmed stimuli and stands.) Corollary: the recon-run claim
  "button presses produce no spew" is INVALIDATED — no presses ever reached the pad; spew during
  real presses is untested in both SI states.
- **SI activation for the synthetic pad is identity + enumeration-order keyed — no GUI needed
  once the identity is known (runner-verified 2026-06-12).** With
  `configset_45e-28e-1ba6d98[g].vdf` present on disk (written when SI was GUI-enabled in a past
  session), a fresh synthetic pad reaches PollState 0→1→2 (active+emitting) on Steam launch —
  PROVIDED it is the only pad and enumerates at controller index 0. Stale holder processes leave
  ghost pads that push the new pad to a higher index and break the configset lookup → SI stays
  off and the situation masquerades as "needs the GUI step". **Env spin-up protocol: kill stale
  holders, create the single synthetic pad BEFORE launching Steam, then verify PollState 2 in
  controller.txt.** (Index-0 + configset-present → PollState 2 is observed; the exact lookup
  mechanism is inferred.)
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
