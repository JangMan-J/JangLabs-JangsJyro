# steam-console recon — result (2026-06-12)

**Run dir:** `runs/20260612T045352Z-steam-console-recon/`  
**Status:** PARTIAL — steam-console recon complete; canary/SI-active phase blocked (see below).

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

## Blocker: SI not activating for synthetic pad without GUI

**OBSERVED.** Steam Input requires a one-time manual GUI action ("Settings → Controller →
Enable Steam Input") to transition a controller from raw/gamepad mode to SI mode. This is
NOT captured in any configset VDF — populating `configset_45e-28e-1ba6d98g.vdf` with a
`413080/autosave:1` entry did NOT change the `Set Account Config Sets N 0 0` output or
trigger PollState 2. The SI-enabled state is stored in Steam's internal database, not in
the on-disk VDF files accessible to us.

**Workaround options for next session:**
1. User performs the GUI "Enable Steam Input" step for the synthetic pad in the nested env
   (one-time; the configset_controller_xbox360.vdf already has `413080/autosave:1` so
   the F9 binding from the Desktop layout will load automatically).
2. Check if `SteamClient.Input` JS API (accessible via CDP) has an enable method — not
   explored in this session.
3. Use the physical 8BitDo (if it reconnects cleanly) — it previously had SI active, so
   PollState 2 would be immediate on reconnect.

## Canary result
**CANARY NOT EXECUTED** — Silent due to SI blocker. XI2 capture on nested `:1`
(`DISPLAY=:1 xi2_capture.py capture`) showed 0 events for all BTN_SOUTH injections.
This is consistent with SI being inactive — not a transient emission silence episode.
The transient silence gotcha (finding canary rule) cannot be confirmed or ruled out
without SI first being active.

## steam-console cvar inventory highlights
Full index: `steam-console-full-index.txt` (557 entries). Controller-relevant:
- `controller_rate = 2000` (500 Hz active poll — confirmed live)
- `controller_idle_poll_interval = 50000` (20 Hz idle)
- `controller_spew_level = 3` (snapshot; can be set live, takes effect immediately)
- `controller_min_activation_time = 0.0333` s — candidate Phase-4 probe target
- `set_spew_level <SpewLevel> <LogLevel>` — affects the CDP spew stream (CONFIRMED)
- No cvar found for: activator decision verbosity, double-tap epoch logging, or SI enable toggle.
