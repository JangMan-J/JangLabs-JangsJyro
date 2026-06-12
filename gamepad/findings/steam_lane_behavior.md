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
  d2d ≈ 130ms r2d fired single); 170ms d2d fires double; 190ms d2d at DTT=190 fired single.
  **Boundary-edge inclusivity is UNRESOLVED and now MOOT.** Conflicting nominal-190 observations
  exist (C2: single; Phase-4 batch 1 trace3: double) with no injector logs to recover actual
  achieved d2d — the signature of timing noise straddling the true edge, not semantics.
  **Product ruling (user, 2026-06-12): the product is "human food" — gamepad schemas for human
  players, who cannot discern ~180ms from ~210ms. Tolerance doctrine: timing equivalence within
  ~10–15 ms is practical equality.** Inclusive-vs-exclusive at the edge is a ≤1-poll-tick
  (~2–4 ms) question, an order below even machine-practical tolerance — spend no further traces
  on it. The epoch itself (d2d vs JSM's proven release-to-down) DOES remain product-relevant:
  the divergence scales with hold duration, which is easily human-perceptible ⇒
  `bounded_approximation` for window translation stands.
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
single) match down-to-down; release-to-down was already ruled out by measurement. (Boundary-edge
inclusivity later proved conflicting across sessions at nominal 190 and was ruled MOOT under the
human-tolerance product doctrine — see the boundary bullet above.)

**Predictions — ALL PINNED (Phase-4 batch 1, 2026-06-12, commit e97e495; raw-layer analysis):**

1. **CONFIRMED.** Singles anchored at first-down + DTT regardless of hold: N=14 across 50–750 ms
   holds, F3 raw press at 192.23 ± 0.84 ms from first-down (DTT=190); pipeline 33.84 ± 0.44 ms.
2. **CONFIRMED.** Double fires at second-down with ~0 ms added latency (5 true doubles,
   d2d 100–185 ms; Regular suppressed throughout).
3. **CONFIRMED.** Held-double: exactly one down at second-down, one up at second-up; NOTHING at
   first-down + DTT even when that boundary fell 30 ms after the second down. The retracted
   re-send axiom is falsified by direct observation.
4. **RESOLVED earlier** at the app plane (user's logger test, 2026-06-11): held binding = one
   held key, no re-send chatter; batch-1 raw captures agree.

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

## Order-dependent edge-activator loss under state-bound co-residency (oracle GUI observation, 2026-06-12)

The user reproduced the Release_Press anomaly **with GUI-native bindings in their own Steam
session** — and generalized it. Observed (app plane, text-field letters; held-key repeats are OS
autorepeat noise; timing not precisely established):

- Start_Press alone, Release_Press alone, and Start+Release+Regular on one button: **all fire
  correctly.** The activators themselves are healthy.
- Add a **state-bound** activator (oracle taxonomy: Long_Press and Double_Press — the two that
  delay other activators on the same binding) and the **edge-fired** pair (Start/Release) becomes
  inconsistent **as a function of activator slot order**:
  - `StartP→A, ReleaseP→B, LongP→C` (press-hold): output `B C C C…` — **Start never fires**, and
    Release fires EARLY (near down, before any physical release, per the reported sequence).
  - Slots swapped (`ReleaseP→A, StartP→B, LongP→C`): output `B A C C…` — **all three fire.**
- Lab correlation: our generated four-activator marker button (order Start, Release, Full,
  Double) showed Start fires / **Release never** — same bug-class, different slot order, different
  victim. **The encoding-fault hypothesis is DISFAVORED: Valve's own GUI bindings reproduce the
  inconsistency.** The user's verdict: "might be a bug" — the oracle cannot explain it from
  mechanics, which is itself signal.
- Claim strength: oracle-observed, GUI/app plane, one swap tested. **CONFOUND (user-flagged
  2026-06-12): slot order is confounded with rebinding-state** — the swap test changed the order
  AND had just rebound the button; the behavior flip could follow either (cf. the soft-pull
  adaptive-state precedent and the transient-silence gotcha: Steam config state is not
  side-effect-free). Open question: does the eat-pattern persist after reconfiguring bindings,
  across configurator enter/exit, and across Steam restarts? Systematic characterization queued:
  **order-permutation matrix** of {Start, Release} × {Long | Double | Full+Double} slot orders,
  synthetic + raw-layer, with controls per cell — fresh disk-load (standard vdf protocol),
  repeat-after-restart, and rebind-without-reorder — to separate order-dependence from
  state-dependence.
- **The GUI slot model (screenshot evidence: `reference/oracle-gui-observations/`):** multiple
  activators render as numbered **"Command 1..N"** slots — order is explicit, ordinal, and
  user-visible, created implicitly by binding order. Real-world configs therefore CARRY these
  orderings everywhere, and authors never think about them ⇒ the hazard zone is not exotic.
  Bonus acquittal: the user's button A binds Release_Press→F2 ALONE — same activator, same key
  as our marker layout — and it fires.
- **Pure order-dependence FALSIFIED (third screenshot + user report, 2026-06-12):** after more
  rebinding churn, the SAME visible order that was broken (Start, Release, Long at slots 1/2/3 —
  numbering reset, ghosts gone) **now fires all three activators** ("now its working...idk").
  The driver is hidden STATE, not visible order. Candidates: (a) file-level ghost/retired slots;
  (b) **Steam's per-controller config cache** ("HID: Add to Config Cache - full cache hit" in
  controller.txt — survives Steam restarts, so it can contaminate even disk-loaded layouts; note
  our clean disk-loaded marker layout still ate Release after a churn-heavy session); (c)
  configurator-session state. The oracle cannot identify the driver from the GUI side — this is
  a state Heisenbug; only controlled state transitions (the matrix protocol, plus possibly
  cache-cold cells) can pin it. Claim strengths: same-order-now-works OBSERVED; what changed
  between observations is NOT controlled (GUI action sequence unrecorded).
- **Ghost slot indices (second screenshot, 2026-06-12): slot numbers are sticky across
  rebinding.** After the user's reconfiguration experiments, button B shows "Executes 3
  Commands" with slots numbered **3, 4, 5** — removed commands retire their indices; new ones
  append. Slot identity is rebinding-history-dependent. **Mechanism candidate:** the bug-class
  may key on absolute slot index or ghost/retired slots rather than visible order (note the
  ever-present `disabled_activators` block in the vdf schema as a possible home for retired
  slots — check the flushed autosave). Matrix implication: our generator writes clean 1..N
  histories — a GUI-evolved layout with ghosts is a DIFFERENT test article than a disk-written
  layout with the same visible order; the matrix's rebind-without-reorder control cell covers
  exactly this axis, and the flushed autosave will show how slots 3/4/5 serialize.
- **Converter implication (human-food relevant):** button configs mixing Start/Release Press with
  Long/Double Press are a HAZARD ZONE — activator loss that depends on an ordering most authors
  never think about. Conversions touching such combos classify no better than
  `degraded_approximation` with the hazard named, and converting INTO such a combo should be
  avoided (anti-Goodhart: don't engineer configs that depend on replicating a probable Steam bug).

## Operational gotchas (Steam lane)

- **xinput keysym aliasing:** F11/F12 print as legacy keysyms **L1/L2** in `xinput test-xi2`
  output — fold them in the normalizer before diffing.
- **Dev-console spew is a dead end for activator tracing (closed 2026-06-12).** With SI active
  and a confirmed double firing in XI2, `controller_spew_level`/`set_spew_level` at 10 exposes
  only HID-layer events (`Switch State` transitions, connect/disconnect) — no activator names,
  no decision events, at any tested level. Don't burn sessions looking; steam-console remains a
  cvar get/set + HID-event tool.
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
