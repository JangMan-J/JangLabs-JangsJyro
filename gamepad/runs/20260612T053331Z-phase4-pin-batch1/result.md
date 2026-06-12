# Phase-4 pin batch 1 — result (2026-06-12)

**Run dir:** `runs/20260612T053331Z-phase4-pin-batch1/`  
**Status:** BATCH 1b COMPLETE — P1–P4 discrimination probes done; F2 still absent; XI2 key-hold illusion explained; awaiting lead gate for pin traces.  
**Backup:** `controller_xbox360.autosave-backup.vdf` (original autosave, 353 lines)  
**Layout active:** `marker_layout.vdf` (button_a→F5, button_b→F6/F7, button_x→F8/F9, button_y→F1/F2/F3/F4)

## Step 1: Layout swap + PollState 2 — COMPLETE (OBSERVED)

VDF protocol followed:
1. Backup autosave → `controller_xbox360.autosave-backup.vdf`
2. `steam -shutdown` → confirmed down
3. Marker layout copied over autosave while Steam down
4. Single synthetic pad (PID 1834411, started 22:20:13, xbox360 identity) already running at index 0
5. Steam relaunch → nested env (:1, wayland-jsmlab)

controller.txt (OBSERVED):
```
[2026-06-11 22:34:05] Local Device Found
[2026-06-11 22:34:05] !! Steam controller device opened for index 0.
[2026-06-11 22:34:06] Controller PollState Changed from 0 to 1
[2026-06-11 22:34:06] Controller PollState Changed from 1 to 2
[2026-06-11 22:34:07] Opted-in Controller Mask for AppId 413080: 1006
```

controller_ui.txt (OBSERVED):
```
[2026-06-11 22:34:07] Loaded Config for Local Selection Path for App ID 413080, Controller 0:
  .../config/413080/controller_xbox360.vdf  (×4)
```
Layout loaded: `marker_layout.vdf` (written as the autosave filename `controller_xbox360.vdf`).

## Step 2: Token verification probe — GATE STOP

### Stimulus confirmation (OBSERVED — holder log, no WARN)
All four presses injected cleanly via control-FIFO, confirmed in holder log:
```
[05:34:32.274Z] press SOUTH 120.0ms (down) / (up)
[05:34:34.276Z] press EAST  120.0ms (down) / (up)
[05:34:36.277Z] press WEST  120.0ms (down) / (up)
[05:34:38.278Z] press NORTH 120.0ms (down) / (up)
```
No WARN lines. All stimuli reached evdev.

### Mapping results (OBSERVED — `token-verify-xi2.jsonl`, 20 events)

| DSL button | vdf button | Expected | Observed | Result |
|------------|------------|----------|----------|--------|
| SOUTH | button_a | Full_Press → F5 | F5 ✓ | PASS |
| EAST  | button_b | Full_Press → F6 | F6 ✓ | PASS |
| WEST  | button_x | Full_Press → F8 | F8 ✓ | PASS |
| NORTH | button_y | Start_Press→F1 | F1 ✓ | PASS |
| NORTH | button_y | Release_Press→F2 | **ABSENT** | **FAIL** |
| NORTH | button_y | Full_Press→F3 at DTT | F3 at +192ms ✓ | PASS |

**F2 (Release_Press) absent after confirmed stimulus — GATE STOP triggered per task spec.**

### Timing detail for NORTH (OBSERVED)
```
+  0.0ms  F1 RawKeyPress  (physical down at evdev)
+ 33.9ms  F1 KeyPress     (SI output at xwayland-keyboard:10)
+ 33.9ms  F1 RawKeyRelease
+192.2ms  F1 KeyRelease   — held 158ms at key layer (anomalous; raw released at +34ms)
+192.3ms  F3 RawKeyPress  — DTT=190ms anchor: +192.3ms from F1 RawKeyPress (within ±3ms)
+226.1ms  F3 KeyPress
```

F3 timing: **OBSERVED, correct** — fires at first-down + 192ms (DTT=190ms ±3ms tolerance).  
F3 hold: **ANOMALOUS** — F3 KeyRelease appears only when xi2_capture terminates (6.8s, 14s, 22s depending on capture window). Physical `up NORTH` at 120ms does NOT release F3. This is reproducible across 3 probes.

F2 (Release_Press): **ABSENT** across 3 probes (30s, 8s, 15s capture windows), all with confirmed `up NORTH` at evdev. Not a capture window issue.

### Hypothesis (INFERRED — not proven)
The `Full_Press` activator on button_y has no explicit `start_held_down` or duration setting, but Steam appears to be holding the output key (F3) in a "held" state tied to the virtual pad button state rather than the physical press event. The `Release_Press` activator (F2) may be suppressed or not firing because the `Full_Press` output is still "held" at the point the physical button releases. This is an activator interaction / ordering issue in Steam's pipeline that the marker_layout.vdf may not be handling correctly.

Alternatively: `Release_Press` fires at physical-up but the output key (F2) is suppressed because the Double_Press window is still open at 120ms (window closes at DTT=190ms, physical up is at 120ms). This is plausible — Steam may suppress Release_Press while the double-tap window is active.

**Builder must investigate whether Release_Press + Full_Press coexistence on the same button with a Double_Press window causes F2 suppression, and whether the layout VDF needs adjustment.**

## Artifacts
- `controller_xbox360.autosave-backup.vdf` — original autosave (pre-batch)
- `token-verify-xi2.jsonl` / `token-verify-xi2.txt` — 20 events, mapping probe
- `north-f2-probe.jsonl` / `north-f2-probe.txt` — F2 targeted 8s probe (8 events)
- `north-hold-probe.jsonl` / `north-hold-probe.txt` — F3 held-state 15s probe (8 events)
- `holder-log-at-stop.txt` — synthetic_gamepad log at stop (no WARNs)
- `controller-txt-at-stop.txt` — controller.txt tail at stop

## Batch 1b: Discrimination probes P1–P4

### Oracle note (lead reading #1, confirmed OBSERVED)
F3 at +192ms in batch 1a was already oracle prediction 1's first confirmation — Full_Press
emission anchored at first-down + DTT=190ms, after physical release at 120ms. P1 extends
this: with 400ms hold (> DTT), F3 RawKeyPress still fires at +192ms (DTT anchor) and
F3 KeyPress (key layer) arrives at +402ms (= physical up). Prediction 1 confirmed across
both sub-DTT and super-DTT hold durations.

### P1: F2 fork discriminator — 400ms hold (OBSERVED)

Hold duration: 400ms (explicit `down NORTH` / 400ms sleep / `up NORTH`).  
Stimulus confirmed (holder log): `down NORTH` at 05:40:46.886Z, `up NORTH` at 05:40:47.288Z.

```
+  0.0ms  F1 RawKeyPress   (physical down)
+ 34.2ms  F1 KeyPress      (key layer, +34ms pipeline latency)
+ 34.2ms  F1 RawKeyRelease
+192.2ms  F1 KeyRelease    (key layer deferred — flushed at DTT moment)
+192.3ms  F3 RawKeyPress   (DTT anchor: +192ms ✓)
+402.3ms  F3 KeyPress      (key layer deferred — flushed at PHYSICAL UP moment)
+402.4ms  F3 RawKeyRelease
+14049ms  F3 KeyRelease    (key layer — deferred to capture exit)
```

**F2 (Release_Press): ABSENT.** Physical up at 400ms; DTT window closed at 190ms.
Window was closed 210ms before physical up — suppressed-while-window-open hypothesis
is **FALSIFIED** (OBSERVED). F2 was free to fire but did not.

**F3 key-layer delivery at +402ms**: the physical up event flushes the pending F3 KeyPress.
F3 KeyRelease deferred to capture exit (14s). F3 RawKeyRelease at raw layer fired immediately
at +402ms — so raw layer correctly reflects the tap; key-layer hold is an artifact.

**Bonus oracle confirmation (INFERRED — consistent with P2):** F3 RawKeyPress fires at
+192ms even though physical press is still held at 400ms. Steam fires the Full_Press
activator AT the DTT boundary regardless of hold state — confirming the oracle's
"emission anchored at first-down + DTT" for sub- and super-DTT holds alike.

### P2: Raw vs key layer audit — 120ms press (OBSERVED)

Full event stream showing raw vs key-layer timing explicitly:

```
Layer       Event            Timing      Interpretation
─────────   ───────────────  ─────────   ──────────────────────────────────────────
raw/master  F1 RawKeyPress   +0.0ms      SI emits F1 at physical down
key/slave   F1 KeyPress      +35.1ms     key-layer delivery deferred — flushed by F1 RawKeyRelease
raw/master  F1 RawKeyRelease +35.1ms     raw-layer releases F1 (34ms raw tap = pipeline latency)
key/slave   F1 KeyRelease    +193.2ms    key-layer release deferred — flushed by F3 RawKeyPress
raw/master  F3 RawKeyPress   +193.2ms    SI emits F3 at DTT (oracle ✓)
key/slave   F3 KeyPress      +227.3ms    key-layer delivery — flushed by F3 RawKeyRelease
raw/master  F3 RawKeyRelease +227.3ms    raw-layer releases F3 immediately after press
key/slave   F3 KeyRelease    +9074ms     key-layer release — deferred to CAPTURE EXIT
```

**Key-layer flush pattern (OBSERVED):** Every key-layer (slave) event is flushed by the
NEXT raw-layer (master) event. The final pending key-layer event has no subsequent raw
event to flush it — it sits in the delivery queue until the client disconnects.

**Pipeline latency (OBSERVED):** 34ms from SI raw emission to key-layer delivery. Matches
the lead's C2 ~35ms figure. Confirmed across all four probes.

**Raw layer is ground truth for timing (OBSERVED):** Raw events (master device) carry
the actual SI emission timestamps. Key events (slave device) carry flush-triggered
delivery timestamps — they are NOT suitable for timing analysis without the raw layer.

### P3: Server state during stuck-F3 (OBSERVED)

`DISPLAY=:1 xinput query-state 6` (xwayland-keyboard:10, slave device) while F3 KeyRelease
pending in capture:

```
All key[0]..key[247] = up
```

**Conclusive: the X server holds NO key state during the stuck-F3 window.** F3 is not
pressed at the server level. The "stuck hold" visible in xi2_capture's event stream is
entirely a per-client delivery queue artifact — not a real server-side key press.

Note: `xinput query-state 3` (master keyboard, id=3) returned `unable to find device '3'`
under Xwayland — master device not directly queryable by xinput in this configuration.
Slave device query is sufficient to confirm server state.

### P4: Client-lifecycle flush test (OBSERVED)

Test design: start capture A → inject press NORTH → F3 stuck in A (verified: 7 events,
F3 KeyPress pending) → start capture B → kill A → observe B.

Result: **B received 0 events** both 0.5s after A's death and 5.5s after. B's own exit
produced 0 events.

**Conclusion (OBSERVED):** F3 KeyRelease does NOT propagate to other XI2 clients when A
disconnects. It is NOT a server-broadcast event. It is generated within A's own client
context — most likely `xinput test-xi2` sends a synthetic all-keys-up release on process
exit (XTEST or EIS cleanup), visible only in A's own delivery stream.

The F3 KeyRelease at capture exit is **a capture-tool artifact**, not real SI output.

### Unified XI2 delivery model (INFERRED from P1–P4)

Steam SI via EIS/Xwayland sends **raw-layer tap pairs**: RawKeyPress immediately followed
by RawKeyRelease, fired atomically at the emission moment (physical-down for Start_Press
tokens, DTT-boundary for Full_Press tokens). The key/slave layer is a delivery layer with
a flush-on-next-event queue: each KeyPress waits for the next raw event to be delivered.
The final open KeyPress flushes only on client disconnect (tool-generated synthetic release).

This means **key-layer events are NOT suitable for precise timing analysis** — their
timestamps reflect queue-flush points, not SI emission points. The raw layer is the
correct timing reference. For the oracle pin traces, raw-layer timestamps must be used.

**F3 KeyRelease in the pin traces will always appear at capture exit** unless a subsequent
SI emission event (F1 of the next press) flushes it first. The traces should use raw-layer
events for all timing comparators.

### F2 (Release_Press) status after batch 1b

**OBSERVED — absent across all probes (120ms × 3, 400ms × 1).** Suppressed-while-window-open
hypothesis falsified (P1). Remaining candidates:
1. **Bad VDF token:** Release_Press activator not correctly configured in marker_layout.vdf
   (builder must verify and produce isolated Release_Press variant if needed).
2. **Full_Press activation state blocks Release_Press:** at physical up (+120/400ms), the
   Full_Press activator is in raw-held state (RawKeyRelease has fired at raw layer but
   key-layer is pending). Steam may treat this as "activator still active" and suppress
   Release_Press. This would be a Steam SI activator interaction, not a token problem.
3. **Release_Press fires but as a raw-layer tap with no key-layer flush:** if Release_Press
   emits at physical-up (+120ms) and there is no subsequent event before capture-exit, its
   F2 RawKeyPress would appear — but F2 RawKeyPress is ABSENT from all captures at all
   layers, ruling out this variant.

**F2 is absent at the raw layer as well** — no F2 RawKeyPress anywhere. This points to
Release_Press not emitting at all, not to a delivery flush issue.

## Pin traces: NOT RUN (gated on batch 1b review)

## Spew-with-SI probe: NOT RUN (gated on pin traces)

## Environment at stop
- Nested KWin `:1` / wayland-jsmlab: RUNNING
- Steam (nested): RUNNING, PollState 2, controller index 0
- Marker layout: ACTIVE in autosave
- Synthetic pad (PID 1834411): RUNNING
