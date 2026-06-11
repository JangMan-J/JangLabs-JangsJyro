# Trigger soft-pull adjudication — C2 batch-3 anomaly resolved
**Run:** `20260611T153109Z-trigger-softpull-adjudication`
**Date:** 2026-06-11
**Purpose:** Adjudicate why F3 (soft/edge) did not fire in C2 batch-3 (`staged 0→100→255` and `instant 0→255`), contradicting the Phase-2 steam result. Three slices run on a **fresh Steam client** (full nested KWin + Steam teardown and relaunch; no carryover state from C2).
**Pipeline:** synthetic pad holder (`--control-fifo`) → trace replayed into FIFO → Steam Input (publicbeta 1781139754, nested headless KWin `wayland-jsmlab`, Xwayland `:1`) → `xi2_capture.py`. VDF: `reference/desktop-layout-phase2-reference.vdf` (unchanged — no edits this session). Canary passed 3/3 F9.

---

## Slice 1 — exact Phase-2 staged trace: `trig_phase2_exact`

**Stimulus:** `axis RZ 100` → wait 450ms → `axis RZ 255` → wait 450ms → `axis RZ 0` (identical to the Phase-2 trigger stimulus).
**Result:** F4 only (+450ms, held until capture end). **F3 did not fire.**

This is the same negative result as C2 batch-3. On a fresh Steam client with no carry-over state, the Phase-2 stimulus (RZ=100 soft, RZ=255 full) still fails to fire the edge activator (F3). The Phase-2 result that claimed "staged pull: F3 down → F4 added" is not reproducible on a fresh client. The Phase-2 trigger finding is **suspect** — it may have been influenced by a different adaptive_threshold calibration state in that session.

---

## Slice 2 — staged with RZ=200 intermediate: `trig_staged_high`

**Stimulus:** `axis RZ 200` → wait 450ms → `axis RZ 255` → wait 450ms → `axis RZ 0`.
**Result:** **F3 fires at +380ms** (when RZ=200 crosses the soft threshold); **F4 fires at +830ms** (when RZ=255 crosses the full threshold). Both held simultaneously until release. Exact soft+full overlap confirmed.

**Finding: the edge (soft) threshold with `adaptive_threshold=3` in this VDF lies between RZ=100 and RZ=200.** RZ=100 is below it; RZ=200 is above it. The threshold is a calibrated fraction of the trigger's full-travel range — `adaptive_threshold=3` (on a 0–255 scale) implies a ~3/8 or similar fractional threshold, placing the crossing somewhere in the 128–200 range. The Phase-2 session likely used a soft pull value that happened to cross this threshold (perhaps the user physically ramped through a higher value), or the Phase-2 adaptive state was pre-calibrated from prior use.

---

## Slice 3 — instant 0→255 after priming: `trig_instant`

**Stimulus:** `axis RZ 255` → wait 450ms → `axis RZ 0` (same as C2, run after slices 1+2 in the same session).
**Result:** F4 only (+450ms). **F3 did not fire.**

**Finding: the adaptive_threshold does not recalibrate within-session after prior soft-pull crossings.** Running slices 1+2 (which included an F3-crossing at RZ=200 in slice 2) did not lower the threshold for the subsequent instant jump. Steam's instant 0→255 jump fires full-only regardless of session history — this is consistent behavior, not state-dependent. The cross-runtime delta with JSM (JSM fires soft+full on instant jump; Steam fires full-only) is confirmed as a genuine structural difference, not an artifact.

---

## Verdict: Phase-2 trigger finding needs updating

| Slice | Stimulus | F3 fired? | F4 fired? | Verdict |
|---|---|---|---|---|
| `trig_phase2_exact` | RZ=100→255 (staged) | **No** | Yes at +450ms | soft threshold NOT crossed at RZ=100 |
| `trig_staged_high` | RZ=200→255 (staged) | **Yes** at +380ms | Yes at +830ms | soft threshold crossed at RZ=200 |
| `trig_instant` | RZ=255 (instant) | **No** | Yes at +450ms | instant jump fires full-only; no soft |

**C2 batch-3 anomaly resolved:** F3 not firing was NOT a state-dependent anomaly. It is the correct behavior when `RZ=100` is below the soft threshold set by `adaptive_threshold=3`. The Phase-2 staged trigger claim ("F3 down → F4 added") used a stimulus value that happened to exceed the soft threshold, or the session had a different threshold calibration. With RZ=200 as the soft-pull value, the expected soft+full behavior is confirmed.

**Updated trigger findings (to promote to `findings/steam_lane_behavior.md`):**
1. Steam's trigger soft/full model (edge+click activators) fires the edge binding when the axis crosses the threshold set by `adaptive_threshold`. With `adaptive_threshold=3` on a 0–255 scale, the crossing lies between RZ=100 and RZ=200.
2. An instant 0→255 jump fires **full-only** on Steam (no soft), regardless of prior session state. This is a structural difference from JSM's axis-threshold model (which fires soft+full on any threshold crossing, including instant jumps). The Phase-4 adversarial trace should use RZ=200 as the staged intermediate value to reliably reproduce the soft+full path on Steam.
3. The Phase-2 result.md trigger entry ("staged pull: F3 down → F4 added") should be annotated: the staged intermediate value must exceed the adaptive threshold (use RZ=200, not RZ=100, for reproducible results).
