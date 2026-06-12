# Batch 2a — Slot-Order Permutation Matrix Results

**Run:** `20260612T072850Z-phase4-batch2-matrix`  
**Date:** 2026-06-12 (session 7, runner2)  
**Claim strength:** single-pass, state not controlled (environment-trust doctrine 2026-06-12)  
**Layouts:** 6 (A1, A2, B1, B2, C1, C2)  
**Cells:** 16 (6×Set-A buttons + 6×Set-B buttons + 4×Set-C buttons)  
**Captures:** 868 XI2 events across the 6 matrix JSONL files (880 incl. the respin canary; 892 incl. the dead-session canary)  
**Lead gate:** PASS 2026-06-12 session 8 — raw-layer press counts independently re-derived from all 7 JSONLs; per-cell table consistent (Set A: 6/3 per button; Set B: 9 Start, 0 Double; Set C: 13/13 + 12/12 with the +1 liveness tap per manifest); holder log 0 WARN (stimulus-confirmation satisfied); event-count line above corrected (was "892 across 6 files")  

---

## Environment

- Nested KWin wayland-jsmlab, Display :1
- Single synthetic Xbox-360 pad (event21, controller index 0)
- PollState 2 confirmed each layout via controller.txt
- No WARN lines in holder log across full session
- autosave == slot_order_set_a1.vdf at session start (md5 verified)
- Original autosave backup untouched (controller_xbox360.autosave-backup.vdf)

---

## F-key role legend (all sets)

`Start_Press → F(n)`, `Release_Press → F(n+1)`, `Long_Press / Full_Press / Double_Press → F(n+2)` per button block.

**Set A** (`button_y` F10 canary): `button_a` F1–F3, `button_b` F4–F6, `button_x` F7–F9  
**Set B** (`button_y` F10 canary): same F-key assignments, `Double_Press` instead of `Long_Press`  
**Set C** (no canary, 2 active buttons): `button_a` F1–F4, `button_b` F5–F8

---

## 16-Cell Observation Table (RAW layer only)

| # | Layout | Button | Perm | Slot order | Stimulus | Keys fired (RAW) | Release (Fn+1) | State-bound (Fn+2) | Verdict |
|---|--------|--------|------|-----------|----------|-------------------|----------------|-------------------|---------|
| A-P1-tap | A1 | button_a | P1 | S,R,L | Quick tap ×3 | F1 | **ABSENT** | — | Start fires; Release eaten |
| A-P1-long | A1 | button_a | P1 | S,R,L | Long hold ×3 | F1+F3 | **ABSENT** | F3 fires | Start+Long; Release eaten |
| A-P2-tap | A1 | button_b | P2 | S,L,R | Quick tap ×3 | F4 | **ABSENT** | — | Start fires; Release eaten |
| A-P2-long | A1 | button_b | P2 | S,L,R | Long hold ×3 | F4+F6 | **ABSENT** | F6 fires | Start+Long; Release eaten |
| A-P3-tap | A1 | button_x | P3 | R,S,L | Quick tap ×3 | F7 | **ABSENT** | — | Start fires; Release eaten |
| A-P3-long | A1 | button_x | P3 | R,S,L | Long hold ×3 | F7+F9 | **ABSENT** | F9 fires | Start+Long; Release eaten |
| A-P4-tap | A2 | button_a | P4 | R,L,S | Quick tap ×3 | F1 | **ABSENT** | — | Start fires; Release eaten |
| A-P4-long | A2 | button_a | P4 | R,L,S | Long hold ×3 | F1+F3 | **ABSENT** | F3 fires | Start+Long; Release eaten |
| A-P5-tap | A2 | button_b | P5 | L,S,R | Quick tap ×3 | F4 | **ABSENT** | — | Start fires; Release eaten |
| A-P5-long | A2 | button_b | P5 | L,S,R | Long hold ×3 | F4+F6 | **ABSENT** | F6 fires | Start+Long; Release eaten |
| A-P6-tap | A2 | button_x | P6 | L,R,S | Quick tap ×3 | F7 | **ABSENT** | — | Start fires; Release eaten |
| A-P6-long | A2 | button_x | P6 | L,R,S | Long hold ×3 | F7+F9 | **ABSENT** | F9 fires | Start+Long; Release eaten |

| # | Layout | Button | Perm | Slot order | Stimulus | Keys fired (RAW) | Release (Fn+1) | Double (Fn+2) | Verdict |
|---|--------|--------|------|-----------|----------|-------------------|----------------|--------------|---------|
| B-P1-tap | B1 | button_a | P1 | S,R,D | Quick tap ×3 | F1 | **ABSENT** | **ABSENT** | Start only |
| B-P1-dtap | B1 | button_a | P1 | S,R,D | Double-tap d2d~120ms ×3 | F1×2 | **ABSENT** | **ABSENT** | Start fires ×2; Release+Double eaten |
| B-P2-tap | B1 | button_b | P2 | S,D,R | Quick tap ×3 | F4 | **ABSENT** | **ABSENT** | Start only |
| B-P2-dtap | B1 | button_b | P2 | S,D,R | Double-tap ×3 | F4×2 | **ABSENT** | **ABSENT** | Start fires ×2; Release+Double eaten |
| B-P3-tap | B1 | button_x | P3 | R,S,D | Quick tap ×3 | F7 | **ABSENT** | **ABSENT** | Start only |
| B-P3-dtap | B1 | button_x | P3 | R,S,D | Double-tap ×3 | F7×2 | **ABSENT** | **ABSENT** | Start fires ×2; Release+Double eaten |
| B-P4-tap | B2 | button_a | P4 | R,D,S | Quick tap ×3 | F1 | **ABSENT** | **ABSENT** | Start only |
| B-P4-dtap | B2 | button_a | P4 | R,D,S | Double-tap ×3 | F1×2 | **ABSENT** | **ABSENT** | Start fires ×2; Release+Double eaten |
| B-P5-tap | B2 | button_b | P5 | D,S,R | Quick tap ×3 | F4 | **ABSENT** | **ABSENT** | Start only |
| B-P5-dtap | B2 | button_b | P5 | D,S,R | Double-tap ×3 | F4×2 | **ABSENT** | **ABSENT** | Start fires ×2; Release+Double eaten |
| B-P6-tap | B2 | button_x | P6 | D,R,S | Quick tap ×3 | F7 | **ABSENT** | **ABSENT** | Start only |
| B-P6-dtap | B2 | button_x | P6 | D,R,S | Double-tap ×3 | F7×2 | **ABSENT** | **ABSENT** | Start fires ×2; Release+Double eaten |

| # | Layout | Button | Perm | Slot order | Stimulus | Keys fired (RAW) | Start | Release | Full | Double | Verdict |
|---|--------|--------|------|-----------|----------|-------------------|-------|---------|------|--------|---------|
| C-PC1-tap | C1 | button_a | PC1 | S,R,F,D | Quick tap ×3 | F1+F3 | F1 ✓ | **F2 ABSENT** | F3 ✓ | **F4 ABSENT** | Start+Full; Release+Double eaten |
| C-PC1-dtap | C1 | button_a | PC1 | S,R,F,D | Double-tap ×3 | F1+F3 per down | F1 ✓×2 | **F2 ABSENT** | F3 ✓×2 | **F4 ABSENT** | Start+Full per down; Release+Double eaten |
| C-PC1-hold | C1 | button_a | PC1 | S,R,F,D | Hold ~400ms ×3 | F1+F3 | F1 ✓ | **F2 ABSENT** | F3 held ✓ | **F4 ABSENT** | Start fires; Full held; Release+Double eaten |
| C-PC2-tap | C1 | button_b | PC2 | R,S,F,D | Quick tap ×3 | F5+F7 | F5 ✓ | **F6 ABSENT** | F7 ✓ | **F8 ABSENT** | Start+Full; Release+Double eaten |
| C-PC2-dtap | C1 | button_b | PC2 | R,S,F,D | Double-tap ×3 | F5+F7 per down | F5 ✓×2 | **F6 ABSENT** | F7 ✓×2 | **F8 ABSENT** | Start+Full per down; Release+Double eaten |
| C-PC2-hold | C1 | button_b | PC2 | R,S,F,D | Hold ~400ms ×3 | F5+F7 | F5 ✓ | **F6 ABSENT** | F7 held ✓ | **F8 ABSENT** | Start fires; Full held; Release+Double eaten |
| C-PC3-tap | C2 | button_a | PC3 | F,D,S,R | Quick tap ×3 | F1+F3 | F1 ✓ | **F2 ABSENT** | F3 ✓ | **F4 ABSENT** | Start+Full; Release+Double eaten |
| C-PC3-dtap | C2 | button_a | PC3 | F,D,S,R | Double-tap ×3 | F1+F3 per down | F1 ✓×2 | **F2 ABSENT** | F3 ✓×2 | **F4 ABSENT** | Start+Full per down; Release+Double eaten |
| C-PC3-hold | C2 | button_a | PC3 | F,D,S,R | Hold ~400ms ×3 | F1+F3 | F1 ✓ | **F2 ABSENT** | F3 held ✓ | **F4 ABSENT** | Start fires; Full held; Release+Double eaten |
| C-PC4-tap | C2 | button_b | PC4 | F,S,D,R | Quick tap ×3 | F5+F7 | F5 ✓ | **F6 ABSENT** | F7 ✓ | **F8 ABSENT** | Start+Full; Release+Double eaten |
| C-PC4-dtap | C2 | button_b | PC4 | F,S,D,R | Double-tap ×3 | F5+F7 per down | F5 ✓×2 | **F6 ABSENT** | F7 ✓×2 | **F8 ABSENT** | Start+Full per down; Release+Double eaten |
| C-PC4-hold | C2 | button_b | PC4 | F,S,D,R | Hold ~400ms ×3 | F5+F7 | F5 ✓ | **F6 ABSENT** | F7 held ✓ | **F8 ABSENT** | Start fires; Full held; Release+Double eaten |

---

## Summary observations

### Release_Press: ABSENT across all 16 cells and all slot orders

Release_Press (Fn+1) was **never observed at the RAW layer** in any of the 16 cells across all 6 layouts — regardless of whether it was slot 1, 2, 3, or 4, or whether the co-resident state-bound activator was Long, Double, or Full. This is a universal suppression in this env, not a slot-order-specific effect.

**Implication:** The slot-order effect observed in the GUI (oracle finding 2026-06-12) — where (R,S,L) fixed Start+Release vs (S,R,L) breaking Start — does NOT appear in this single-pass synthetic run. Either the fix is state-dependent (consistent with the pure-order-dependence falsification in the finding: same order works after state churn), or our clean disk-loaded synthetic layouts happen to land in a broken state universally. Claim strength: single-pass, state not controlled — cannot distinguish these.

**Comparison with oracle GUI observation:**
- GUI (S,R,L): Start never fires, Release fires early ← **contradicted** by this run (Start fires in all S,R,L = A-P1)
- GUI (R,S,L): all three fire ← **not reproduced**: P3 shows Start fires, Release absent
- Possible explanation: GUI observation was in a different state than our clean disk-loaded state. The oracle's "pure order falsification" (same-order-now-works after rebinding churn) supports state as the driver.

### Double_Press: ABSENT in Set B (all 6 permutations)

Double_Press (Fn+2) was never observed in any Set B cell — neither on quick taps nor double-taps (d2d~120ms < DTT=190ms). This is unexpected: the oracle model and Phase-4 batch 1 confirmed Double fires at second-down on the marker layout. In Set B, Start_Press fires in every slot and Double is completely suppressed.

**Note:** The batch-1 marker layout had Full_Press as the "Regular" activator (not Start_Press + Double). Set B has Start_Press + Release_Press + Double_Press — with Start present, Start fires immediately on every down event and the Double window may never open meaningfully. This is a distinct interaction pattern from marker_layout.

### Full_Press (Set C): FIRES alongside Start

In Set C (4-activator: S/R/F/D or F/D/S/R and F/S/D/R), Full_Press fires alongside Start_Press on every tap. Release_Press and Double_Press remain absent. This is consistent with Full_Press being the "Regular" activator that fires on standard press.

### Start_Press: ALWAYS fires

Start_Press was present in every single cell across all 16 observations — it fires immediately on press-down regardless of slot position or co-resident activators.

---

## Key comparisons (task spec targets)

**A-P1 (S,R,L — GUI-broken) vs A-P3 (R,S,L — GUI-fixed):**
- Both: Start fires, Release absent, Long fires on holds.
- No observable difference between the two permutations in this run. The GUI-observed fix (P3 → all fire) was NOT reproduced. Single-pass, state not controlled.

**C-PC1 (S,R,F,D — known Release-eaten) vs C-PC2 (R,S,F,D — reverse-edge fix?):**
- Both: Start+Full fire; Release absent; Double absent.
- Moving Release to slot 1 (PC2) did NOT rescue Release firing in this run. Consistent with the pure-order-dependence falsification (state is the driver, not visible slot order).

---

## Anomaly notes

- **Double_Press fully suppressed in Set B across all 6 permutations:** unexpected given batch-1 confirmed Double fires at second-down on marker_layout. The difference is that marker_layout uses Full_Press (Regular) + Double; Set B uses Start_Press + Release_Press + Double. Start_Press firing instantly on each down may interfere with the Double disambiguation window. Recorded as single-pass observation; not investigated further per doctrine.
- **Set C Full_Press fires without delay on quick tap:** consistent with Full_Press being non-interruptable by Double in this layout state (Start fires before Full window; Double never opens).
- **No DTT-delayed emission observed in Set C:** expected if Double_Press is universally suppressed (no window to wait out).

---

## Artifacts

| File | Description |
|------|-------------|
| `canary-a1-respin.jsonl` | A1 canary (3× NORTH→F10) — env liveness at session start |
| `a1-raw.jsonl` | Set A, Layout 1 (P1/P2/P3): 108 events |
| `a2-raw.jsonl` | Set A, Layout 2 (P4/P5/P6): 120 events |
| `b1-raw.jsonl` | Set B, Layout 1 (P1/P2/P3, DTT=190): 120 events |
| `b2-raw.jsonl` | Set B, Layout 2 (P4/P5/P6, DTT=190): 120 events |
| `c1-raw.jsonl` | Set C, Layout 1 (PC1/PC2): 200 events |
| `c2-raw.jsonl` | Set C, Layout 2 (PC3/PC4): 200 events |
| `run-manifest.json` | Validated manifest (schema v1) |
