# Steamworks Steam Input docs — local snapshots

Raw HTML snapshots of the official Steam Input partner documentation, saved **2026-06-11**
(`curl -sL`, no auth required). Primary-source reference for activator/input-mode semantics;
pinned here because partner-site pages drift and the lab cites exact behavioral sentences
(e.g. the `Interruptable` suppression rule quoted in `../../findings/steam_lane_behavior.md`).

Source root: `https://partner.steamgames.com/doc/features/steam_controller`

| File | Page |
|---|---|
| `steam_controller.html` | landing / table of contents |
| `activators.html` | activator types + settings (Regular/Long/Double/Start/Release/Chorded; Interruptable, Turbo, Toggle, Cycle, Fire delays) |
| `concepts.html` | general concepts |
| `input_source.html` / `input_source_modes.html` | input sources and their modes (dpad, joystick, trigger…) |
| `mode_shifting.html` | mode shifts |
| `action_set_layers.html` | action set layers (Phase-4 `remove_layer` gotcha) |
| `legacy_mode.html` | legacy keyboard/mouse bindings — the world our desktop-layout vdf lives in |
| `iga_file.html` / `action_manifest_file.html` | in-game actions / action manifest (the non-legacy config world) |
| `device_x360_controller.html` | Xbox-360 device page (the synthetic pad's identity) |

Lab discipline applies: these are **naming/mechanism references and hypotheses** — runtime
traces remain authoritative for behavior (`mapper-conversion-lab-plan.md` §2).
