# Chunk C2 — Steam-lane boundary + interruptable traces
**Run:** `20260611T151747Z-chunk-c2-steam-boundary`
**Date:** 2026-06-11
**Pipeline:** synthetic pad holder (`--control-fifo /tmp/synthetic_pad_ctrl`) → trace replayed into FIFO → Steam Input (publicbeta 1781139754, nested headless KWin `wayland-jsmlab`, Xwayland `:1`) → `xi2_capture.py` (XI2 output plane) + `evdev_capture.py` (negative control)
**VDF state:** started from `reference/desktop-layout-phase2-reference.vdf` (confirmed exact match at run start); VDF restored to reference state after batch 4. Intermediate backups at `.vdf.bak-c2` and `.vdf.bak-c2-b4-wrong`.
**Canary protocol:** digital slice (South → F9) run first every sub-session (before batches 1-3; before batch 4 after VDF relaunch). All canary runs passed (3/3 F9 pairs).
**Key aliasing:** Steam emits F11 as keysym `L1`, F12 as keysym `L2` in `xinput test-xi2` — folded by `normalize_capture.py` to F11/F12.

---

## Batch 1 — long-press boundary (slice: `taphold_boundary`)

**Bindings:** East (button_b): Full_Press → F10; Long_Press → F11 (default Long Press Time = 450ms, interruptable=1 on Full_Press by default)
**Presses:** 430ms, 450ms, 470ms

**Results:**
| Duration | Steam output | Verdict |
|---|---|---|
| 430ms | F10 (tap on release) | tap — expected |
| 450ms | F11 (hold) | **hold fires AT 450ms exactly** |
| 470ms | F11 (hold) | hold — expected |

**Finding:** Steam's Long Press Time boundary is **inclusive at the threshold**: a 450ms press fires the hold binding (F11) and suppresses the regular (F10). The default Long Press Time is 450ms. This contrasts with JSM where the effective boundary sits slightly above `HOLD_PRESS_TIME` due to polling granularity (~155ms nominal still gives tap for HOLD_PRESS_TIME=150). **Cross-runtime delta for the comparator:** Steam hold boundary = `>= long_press_time` (inclusive); JSM hold boundary = `> HOLD_PRESS_TIME + ~1 poll interval` (exclusive with jitter). The converter expressing a Long Press Time must account for this: a Steam binding at 450ms may behave as ~155ms in JSM with HOLD_PRESS_TIME=150 but the effective JSM floor is higher by the poll margin.

**Verdict:** `cross-runtime timing delta` — boundary semantics differ: Steam inclusive at threshold, JSM exclusive with poll-interval offset.

---

## Batch 2 — double-tap boundary (slice: `doublepress_boundary`)

**Bindings:** North (button_y): Full_Press → F12; Double_Press → F7 (Double Tap Time = 190ms)
**Gaps probed (first-down to second-down):** 170ms (60ms hold + 110ms wait), 190ms (60ms hold + 130ms wait), 210ms (60ms hold + 150ms wait)

**Results (normalized):**
| Gap (down-to-down) | Steam output | Verdict |
|---|---|---|
| 170ms | F7 (double binding, base suppressed) | double fired |
| 190ms | F12 + F12 (two singles) | **outside window at 190ms** |
| 210ms | F12 + F12 (two singles) | outside window — expected |

**Note on double-F12 pattern:** each single press emits F12 twice — once on the first press release (brief ~34ms hold) and once on a delayed second fire (~952ms hold); this is Steam's double-tap evaluation logic deferring the base binding to confirm no second press is coming.

**Finding:** Steam Double Tap Time boundary is **exclusive at the threshold**: a 190ms down-to-down gap (with 60ms first press hold, so 130ms release-to-second-down) falls OUTSIDE the double window and fires two singles. The double window closes before 190ms. **This also means the measurement reference is down-to-down (first press-down to second press-down)**, not release-to-down — because 190ms down-to-down with 60ms hold = 130ms release-to-down, which is well inside 190ms; yet it fired as singles. The window is `< 190ms` measured down-to-down.

**Converter implication:** Steam double-press window is measured from first press-down to second press-down. Default Double Tap Time = 190ms. JSM DBL_PRESS_WINDOW = 150ms default. Double-press bindings need both parameters adjusted to match — and the boundaries are exclusive (< not <=) on Steam's side.

**Verdict:** `cross-runtime timing delta` — window semantics: Steam exclusive (< threshold, measured down-to-down); JSM boundary unclear (see C1 batch 2 anomaly where even 160ms gap still fired double — needs wider probe to find JSM's actual boundary).

---

## Batch 3 — trigger ramp staged vs instant (slice: `trigramp`)

**Bindings:** Right trigger (group 2): edge → F3 (soft); click → F4 (full). adaptive_threshold = 3.
**Stimuli:** staged (axis RZ=100, wait 450ms, RZ=255, wait 450ms, RZ=0); instant (RZ=255, wait 450ms, RZ=0)

**Results:**
| Stimulus | Steam output | Verdict |
|---|---|---|
| Staged 0→100→255 | F4 only (fires when RZ=255) | soft (F3) did NOT fire |
| Instant 0→255 | F4 only | same — F4 only, no F3 |

**Finding — contradiction with Phase-2 result:** The Phase-2 steam result.md (same VDF, same bindings) stated "staged pull: F3 down → F4 added → both released." This run shows **F3 never fires** for either staged or instant pull. Both ramps emit only F4. The adaptive_threshold=3 may be why the edge/soft threshold is never crossed by an RZ=100 value. The phase-2 result may have been from a different trigger threshold or VDF state where adaptive_threshold was lower, or the RZ=100 value was sufficient in that session.

**Action required (escalate to orchestrator):** This is a contradiction between this run and phase-2 findings. The trigger soft/full Steam finding needs re-examination. Possible explanations: (a) adaptive_threshold=3 requires a higher RZ value than 100 to fire the edge activator; (b) the phase-2 session used a different threshold or VDF revision; (c) the staged ramp in phase-2 used a higher RZ soft-pull value. A follow-up run with RZ=200 as the staged intermediate value may resolve it.

**Verdict:** `anomaly / contradiction` — F3 (soft/edge) did not fire in either ramp. Contradicts Phase-2 steam result. Do not promote to findings until resolved.

---

## Batch 4 — interruptable=0 on Full_Press (slice: `taphold_interruptable_off`)

**Context:** Two sub-runs performed. First run (wrong): `interruptable=0` added to Long_Press settings → no behavioral change (Long_Press is not the activator controlled by the doc's claim). Second run (correct): `interruptable=0` added to Full_Press settings instead → hypothesis confirmed.
**VDF edit:** added `"settings" { "interruptable" "0" }` to `button_b`'s `Full_Press` activator. Protocol: backup → edit → `steam -shutdown` → relaunch nested → canary → run.

**Results (second/correct run, from raw event analysis):**
| Press | Steam output | Verdict |
|---|---|---|
| Short press (120ms) | F10 only | correct — regular press below hold threshold |
| Long press (600ms) | F10 fires on press-down, F11 fires at 450ms threshold; F10 released ~when F11 fires; F11 holds | **both Regular and Long fire** |

**Finding (confirms Steamworks doc hypothesis):** With `interruptable=0` on Full_Press: the Regular binding (F10) fires immediately on press-down and is NOT suppressed when the Long Press (F11) fires at the threshold. Both F10 and F11 are active simultaneously during the long press. This is the documented `interruptable` mechanism: *"Any interruptable activators on the same button will not fire if a long/double press is fired."* Default `interruptable=1` on Full_Press suppresses it; `interruptable=0` lets it fire alongside.

**Converter implication (important):** The converter cannot assume tap/hold maps to JSM `E = A B` (tap-then-hold exclusive). If a Steam layout has `interruptable=0` on the Regular activator, the mapping is Regular-always-fires + Long-fires-at-threshold — a different JSM construct. The converter must read the `interruptable` vdf parameter per-activator, not assume the default. This upgrades the `interruptable` flag from a Phase-4 gotcha to a **Phase-3 schema requirement**: the `normalized-stream` and `delta` schemas must carry `interruptable` state.

**Verdict:** `hypothesis confirmed` — `interruptable` is a load-bearing vdf parameter for the tap/hold mechanic. Steamworks doc claim verified by trace.

---

## Trigger ramp anomaly — follow-up recommendation

Run a follow-up `trigramp_highsoft` trace with `axis RZ 200` as the staged intermediate to test whether adaptive_threshold=3 sets a higher soft threshold than RZ=100 can cross. If F3 fires at RZ=200, the phase-2 result was from a higher soft-pull value; if still no F3, the VDF needs investigation (edge activator may require a specific trigger mode config). Do NOT update `findings/steam_lane_behavior.md` trigger entry until this is resolved.

---

## Summary

| Slice | Result | Classification |
|---|---|---|
| `taphold_boundary` | Steam hold fires at exactly 450ms (inclusive); JSM fires above HOLD_PRESS_TIME + poll margin (exclusive with jitter) | `cross-runtime timing delta` |
| `doublepress_boundary` | Steam double window exclusive at 190ms measured down-to-down; 190ms = outside, 170ms = inside | `cross-runtime timing delta` |
| `trigramp` | F3 (soft/edge) never fires (neither staged nor instant) — contradicts Phase-2 result | `anomaly — escalate to orchestrator` |
| `taphold_interruptable_off` | interruptable=0 on Full_Press causes Regular to fire alongside Long — confirms Steamworks doc claim | `hypothesis confirmed; schema implication` |
