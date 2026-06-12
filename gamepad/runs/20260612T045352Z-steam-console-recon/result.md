# steam-console recon + SI-activation repair — result (2026-06-12)

**Run dir:** `runs/20260612T045352Z-steam-console-recon/`  
**Status:** COMPLETE — steam-console recon complete (Task #1); SI activation repaired without GUI (Task #3 Attempt A success); canary PASS confirmed.

## Environment

- Steam: native pacman, publicbeta 1781212412, running on nested KWin `:1` (wayland-jsmlab)
  via `tools/steam-virtual-env.sh` — seat-free lane confirmed operational.
- CDP port 8080: **reachable**, `SharedJSContext` target present throughout.
- `steam-console --setup` flag: already present (`~/.steam/steam/.cef-enable-remote-debugging`).
- Synthetic pad (vid=0x045e/pid=0x028e "Microsoft X-Box 360 pad"): created, recognized by
  Steam (`Local Device Found`, opened at controller index 2), but **Steam Input NOT activated**
  (see blocker below).
- Physical 8BitDo (vid=0x2dc8, pid=0x6012): present at session start but disconnected
  (hid_read failure at 22:01) during our first probe window; did not reconnect.

## steam-console recon: answers

### 1. Can steam-console connect and send/receive?
**YES — OBSERVED.** CDP connects to `SharedJSContext`, `SteamClient.Console.RegisterForSpewOutput`
binding fires. Command responses (`find controller_rate`, `find controller_spew_level`) arrive
via the spew stream within ~1s. `--complete` prefix autocomplete works offline.

### 2. What does controller_spew_level control?
**OBSERVED/PARTIALLY CHARACTERIZED.** At the default level 3, the spew stream is **silent** 
(no ambient controller chatter). At levels 5–9 (`controller_spew_level N` AND `set_spew_level N N`),
the stream is also silent when no controller events are occurring. Exception: `SinkAdded` audio
events appear at level 5+ during Steam's audio subsystem init. Controller connection/disconnection
events DO appear in the spew at level 10 when a HIDAPI-connected pad (the physical 8BitDo) connects
or disconnects — specifically: "Removing HIDAPI device", "Custom SDL Mapping", "Destroyed virtual
controller", "Controller device closed after hid_read failure", "Controller PollState Changed".

### 3. Can cranked spew expose activator DECISIONS (double-tap epoch, suppression, emission timing)?
**NOT DETERMINED — conditional on SI being active.** During all our probe windows, Steam Input
was NOT active for the synthetic pad (SI disabled; see blocker). Button injections with SI
off produced **zero spew** at levels 3–9. We cannot rule out that activator decision events
appear at high spew levels when SI IS active — that question remains open for the next session
(requires the GUI "Enable Steam Input" step first).

The controller.txt file (written by Steam's controller subsystem, separate from CDP spew)
records config-set loading and PollState transitions but NOT per-press activator decisions —
confirming that activation decision logging, if it exists, would have to come through the CDP
spew channel or is simply not exposed.

### 4. What is the `Set Account Config Sets N A B` pattern?
**INFERRED (not proven):** Three params: controller_index, config_set_A, config_set_B (or
SI_mode). Always `N 0 0` for every controller we've seen. This fires during the config
activation pipeline (after `HID: Add to Config Cache - full cache hit`) but does NOT trigger
PollState change. Whether `B=0` means "SI disabled" is plausible but unproven.

### 5. PollState semantics (OBSERVED from controller.txt):
- PollState 0 = no controller / disconnected
- PollState 1 = controller opened, config loading
- PollState 2 = **active + emitting** (SI output live) — only reached for the physical 8BitDo
  in prior sessions, and for two ghost synthetic pads in the current session that were 
  leftover from a previous Steam launch.
- The synthetic pad (index 2) never reached PollState 2 in any of our current launch cycles.

## Task #3: SI-activation repair — Attempt A SUCCESS

### Root cause of all prior XI2 silence (OBSERVED)
All canary captures in prior attempts reported 0 events. Root cause identified: **wrong
DSL syntax** in `synthetic_gamepad.py` control-fifo. The DSL uses short button names
WITHOUT the `BTN_` prefix — `press SOUTH` is correct; `press BTN_SOUTH` silently fails
with `WARN bad action 'press BTN_SOUTH': 'BTN_SOUTH'` and injects nothing to evdev. All
prior FIFO writes used `BTN_SOUTH` (evdev convention) — the pad never fired at all.
Discovery: reading `synthetic_gamepad.py` source line 20 (`Buttons: SOUTH EAST NORTH...`).

This was entirely independent of SI state — the pad was also silent in all prior spew and
evdev capture windows, not because SI was off, but because the button name was wrong.

### Attempt A mechanism (OBSERVED)
**Ordered steps that achieved PollState 2:**
1. Kill all ghost synthetic pad processes (multiple `python3 tools/synthetic_gamepad.py`
   processes leftover from prior runs — had created phantom pad slots at indices > 0).
2. Shut down Steam cleanly.
3. Create ONE synthetic pad (xbox360 identity) FIRST — before Steam launch.
4. Relaunch Steam inside nested env (`DISPLAY=:1 WAYLAND_DISPLAY=wayland-jsmlab setsid steam`).
5. Steam enumerates the uinput pad as index 0 (no competing ghost pads), finds the
   pre-existing `configset_45e-28e-1ba6d98.vdf` on disk (written session-4), and activates SI.

**controller.txt evidence (OBSERVED):**
```
[2026-06-11 22:20:30] Local Device Found
[2026-06-11 22:20:30] !! Steam controller device opened for index 0.
[2026-06-11 22:20:30] Controller PollState Changed from 0 to 1
[2026-06-11 22:20:30] Controller 0 mapping uses xinput : false
[2026-06-11 22:20:30] Controller PollState Changed from 1 to 2
[2026-06-11 22:20:30] Opted-in Controller Mask for AppId 0: 1006
[2026-06-11 22:20:32] Opted-in Controller Mask for AppId 413080: 1006
```

**controller_ui.txt evidence (OBSERVED):**
```
[2026-06-11 22:20:32] Loaded Config for Local Selection Path for App ID 413080, Controller 0:
  .../config/413080/controller_xbox360.vdf  (×4)
```
Layout loaded: `controller_xbox360.vdf` (revision 39), binding `button_a → key_press F9`.

**Why the configset_45e-28e-1ba6d98.vdf file matters (INFERRED from behavior):**
Its presence on disk (even with empty `controller_config {}`) is what Steam uses to
identify a previously-seen pad identity and skip the GUI "Enable SI" step. The 'g'-suffix
variant (`configset_45e-28e-1ba6d98g.vdf`) appears to be written when SI was enabled via
GUI in a prior session — both files exist and together signal SI-enabled for this pad.

**Ghost pad root cause (INFERRED):** Multiple synthetic pad processes running simultaneously
gave Steam multiple uinput devices with the same vid/pid. Steam assigned them to higher
indices and the configset hash lookup resolved to a different internal slot. Single clean
pad at index 0 avoids this ambiguity.

## Canary result — PASS (OBSERVED)
**Artifact:** `canary-xi2-correct.jsonl` (20 events), `canary-xi2-correct.txt`

5× `echo "press SOUTH" > $FIFO` (correct DSL syntax) while XI2 capture running on DISPLAY=:1.

```
Total events: 20, F9: 20, KeyPress: 5, KeyRelease: 5
Device: {'↳ xwayland-keyboard:10'}
```

Sample events:
```json
{"t": 1781241869.081829, "event": "RawKeyPress",   "dev": "⎣ Virtual core keyboard",   "code": "F9"}
{"t": 1781241869.204149, "event": "KeyPress",       "dev": "↳ xwayland-keyboard:10",    "code": "F9"}
{"t": 1781241869.204305, "event": "RawKeyRelease",  "dev": "⎣ Virtual core keyboard",   "code": "F9"}
{"t": 1781241869.484114, "event": "KeyRelease",     "dev": "↳ xwayland-keyboard:10",    "code": "F9"}
```

SI output arrives at `xwayland-keyboard:10` (the Xwayland seat on `:1`), NOT at evdev.
Emission latency: ~120 ms RawKeyPress→KeyRelease (consistent with `press` default 120 ms hold).

**The canary rule holds:** the prior "silent" captures were NOT transient emission silence —
they were silent because the stimulus never reached evdev (wrong DSL syntax). With correct
syntax and SI active, the canary fires deterministically.

## Environment state at session end
- Nested KWin `:1` / wayland-jsmlab: RUNNING
- Steam (nested): RUNNING, PollState 2 for synthetic pad at index 0
- Synthetic pad (pid varies): RUNNING
- Ready for Phase-4 trace batch (gated on lead review)

## steam-console cvar inventory highlights
Full index: `steam-console-full-index.txt` (557 entries). Controller-relevant:
- `controller_rate = 2000` (500 Hz active poll — confirmed live)
- `controller_idle_poll_interval = 50000` (20 Hz idle)
- `controller_spew_level = 3` (snapshot; can be set live, takes effect immediately)
- `controller_min_activation_time = 0.0333` s — candidate Phase-4 probe target
- `set_spew_level <SpewLevel> <LogLevel>` — affects the CDP spew stream (CONFIRMED)
- No cvar found for: activator decision verbosity, double-tap epoch logging, or SI enable toggle.
