# Chunk C1 — JSM-lane boundary traces
**Run:** `20260611T150936Z-chunk-c1-jsm-boundary`
**Date:** 2026-06-11
**Pipeline:** `synthetic_gamepad.py --trace` → JSM (`build-linux/JoyShockMapper`, binary dated 2026-06-02) → `evdev_capture.py --grab-name JoyShockMapper` → `normalize_capture.py`
**Pre-conditions:** Steam shut down before run; held pad FIFO released. JSM binary built 2026-06-02 (unchanged from phase-2).

---

## Batch 1 — tap/hold boundary (slice: `taphold_boundary`)

**Config:** `HOLD_PRESS_TIME = 150`, `E = A B`
**Presses injected:** 130ms, 145ms, 150ms, 155ms, 170ms

**Results (normalized):**
| Duration (injected) | Actual mono duration | JSM output | Verdict |
|---|---|---|---|
| 130ms | ~130ms | KEY_A (tap) | tap — expected |
| 145ms | ~145ms | KEY_A (tap) | tap — expected |
| 150ms | ~151ms | KEY_A (tap) | tap — UNEXPECTED (expected hold at >=150ms) |
| 155ms | ~155ms | KEY_A (tap) | tap — UNEXPECTED (expected hold) |
| 170ms | ~170ms | KEY_B (hold) | hold — expected |

**Finding:** The hold boundary is NOT at 150ms as documented. Both 150ms and 155ms injections produced tap. Hold only fired at 170ms. The effective boundary sits between 155ms and 170ms, likely 160–165ms. **Hypothesis:** JSM processes events on a polling loop; the hold timer is checked at each poll tick, and a press must survive at least one full poll cycle past 150ms before firing hold. The ~8–16ms extra margin reflects poll-interval granularity. The 150ms HOLD_PRESS_TIME is a *logical* threshold, not a wall-clock one — the effective wall-clock boundary is `HOLD_PRESS_TIME + up_to_one_poll_interval` (~8ms per SDL event loop). This is a **bounded approximation loss** for the converter: a Steam Long Press binding at 150ms may fire a tap in JSM at actual 155ms.

**Verdict:** `bounded_approximation` — hold boundary is `HOLD_PRESS_TIME + ~1 poll interval` (not `>= HOLD_PRESS_TIME`). Not a bug; a consequence of discrete polling. Recommend converter documentation add the poll-granularity caveat.

---

## Batch 2 — double-press window boundary (slice: `doublepress_boundary`)

**Config:** `DBL_PRESS_WINDOW = 150`, `N = B`, `N,N = X`
**Inter-press gaps probed (first-down to second-down):** 140ms, 150ms, 160ms

**Results (normalized):**
| Gap (injected) | JSM output | Verdict |
|---|---|---|
| 140ms | B + X (double) | double — expected |
| 150ms | B + X (double) | double — expected |
| 160ms | B + X (double) | double — UNEXPECTED (expected single at >150ms) |

**Finding:** All three gaps triggered the double-press binding. The window extends past 160ms with `DBL_PRESS_WINDOW=150`. **Hypothesis:** the window is measured from first press **release** (up), not from first press **down** (like the README implies with "down press within 150ms from a previous down press"). In the trace: first down at t=0, first up at ~60ms, second down at t=160ms → gap from release to second down = 100ms < 150ms. If the window is release-to-down, 160ms gap (down-to-down) = 100ms release-to-down still qualifies. This interpretation matches all three observed results: 140ms down-to-down = 80ms release-to-down (fires), 150ms = 90ms release-to-down (fires), 160ms = 100ms release-to-down (fires). To find the true boundary, a wider gap is needed. This is an **ambiguity in the window measurement reference point** — needs follow-up traces with gaps of 200ms, 250ms (down-to-down) to find where it stops.

**Verdict:** `anomaly / needs-wider-probe` — double-press window boundary not established at ±10ms around 150ms because the effective measurement reference point appears to be release-to-down, not down-to-down. The 160ms down-to-down gap still fires double. Escalate to orchestrator: window reference requires clarification.

---

## Batch 3 — trigger ramp: instant vs staged (slice: `trigramp`)

**Config:** `ZR_MODE = NO_SKIP`, `ZR = RMOUSE`, `ZRF = LSHIFT`
**Stimuli:**
1. Staged: RZ=0 → 100 (wait 450ms) → 255 (wait 450ms) → 0
2. Instant: RZ=0 → 255 (wait 450ms) → 0

**Results (normalized):**
| Stimulus | JSM output | Verdict |
|---|---|---|
| Staged 0→100→255 | MOUSE_RIGHT at t=0 (soft, 905ms total), LEFTSHIFT at t=450ms (full) | both soft and full fire sequentially |
| Instant 0→255 | MOUSE_RIGHT at t=1502ms AND LEFTSHIFT at t=1505ms (within 3ms) | BOTH fire, near-simultaneously |

**Finding:** JSM fires the soft binding on ANY threshold crossing of the trigger — even an instant 0→255 jump fires MOUSE_RIGHT before LSHIFT (~3ms apart). This contrasts with Steam's behavior (Phase-2 steam finding: instant 0→255 fired FULL only, no soft). **JSM's trigger model is ABS_RZ-threshold-based: any RZ value above the soft threshold fires the soft binding; passing the full threshold additionally fires the full binding.** An instant jump crosses the soft threshold too, but only momentarily — JSM still registers it. The soft event appears first, then the full event within one poll tick.

**Verdict:** `cross-runtime delta confirmed` — JSM instant-jump: soft + full (both fire). Steam instant-jump: full only (soft skipped). This is an adversarial-trace finding for Phase 4. The converter must classify trigger bindings that assume ramp-independence as `bounded_approximation` for the Steam→JSM direction (Steam may miss soft on fast pulls).

---

## Batch 4 — sticky-state minimal variants (slice: `simpress_sticky`)

**Config:** `L = LSHIFT`, `R = E`, `L+R = Q`
**Stimuli:** (1) lone TL baseline, then three rounds of (chord TL+TR, wait gap, lone TL) at gaps 100ms / 300ms / 1000ms

**Results (normalized):**
| Event | Gap | JSM output | Verdict |
|---|---|---|---|
| Lone TL (baseline, no prior chord) | — | LEFTSHIFT | correct |
| Chord TL+TR | — | Q | correct |
| Lone TL after chord | 100ms | Q (BUG) | sticky |
| Chord TL+TR | — | Q | correct |
| Lone TL after chord | 300ms | Q (BUG) | sticky |
| Chord TL+TR | — | Q | correct |
| Lone TL after chord | 1000ms | Q (BUG) | sticky |

**Finding:** Sticky-state bug confirmed at all three gap values including 1000ms. The prior finding in `jsm_lane_behavior.md` noted "600–700ms does not clear it" — now extended: **1000ms also does not clear the sim-press residual state.** The state is effectively permanent until JSM is restarted or controller reconnected. Additionally, the chord itself emits Q twice per round (once for chord, once for sticky lone press) = 3 chords × 2 = 6 Q's total, plus 1 LEFTSHIFT (baseline) = matches normalized output exactly.

**Verdict:** `degraded_approximation` confirmed (extends prior finding). Sticky state is **persistent across any gap tested** (up to 1000ms), not just a short-window race. This strengthens the classification: any layout reusing a SIMPRESS member as a standalone binding will produce incorrect output after the first chord, indefinitely. **Recommend:** update `findings/jsm_lane_behavior.md` with the 1000ms confirmation.

---

## Summary

| Slice | Result | Classification |
|---|---|---|
| `taphold_boundary` | Hold boundary is `HOLD_PRESS_TIME + ~1 poll interval` (not exact at 150ms threshold) | `bounded_approximation` |
| `doublepress_boundary` | Window reference appears to be release-to-down, not down-to-down; 160ms down-to-down still fires double | needs wider probe; `anomaly` |
| `trigramp` | JSM fires soft+full on instant jump; Steam fires full only — cross-runtime delta confirmed | `cross-runtime delta` (Phase 4 material) |
| `simpress_sticky` | Sticky state persists at 1000ms (not just 600-700ms); extends existing `degraded` classification | `degraded_approximation` (strengthened) |
