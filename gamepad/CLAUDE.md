# gamepad — agent conventions

> **Lab scope — `gamepad/`** · a research subdirectory inside the [`JangsJyro`](https://github.com/JangMan-J/JangLabs-JangsJyro) repo (the JoyShockMapper fork, branch `branch-a-port`). This file is the authority for work *inside this lab*; the parent repo's entry doc is [`../AGENTS.md`](../AGENTS.md). The JSM source this lab researches is the **parent tree itself** (`../`) — not a sibling, not vendored: read it in place at `../JoyShockMapper/`, `../configs/`, `../docs/`. Don't edit the parent fork's build/source from here unless the task is explicitly about JSM itself.

## Read first

1. [`README.md`](./README.md) — current focus and lab layout.
2. [`8bitdo-ultimate2-arch-linux-troubleshooting.md`](./8bitdo-ultimate2-arch-linux-troubleshooting.md) — current investigation. Living doc; update as steps land.
3. [`../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md`](../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md) — long-term direction (Steam-Input-vs-JSM behavioral lab). Canonical design spec, preserved in the parent tree; not active.

## What changed

Earlier sessions accumulated material from a Windows-side JSM build effort (branch-a-port cherry-picks, SDL3 source verification) and an Arc-Raiders-specific Steam Input layout investigation. **The Windows JSM saga is concluded and removed.** Don't reintroduce it speculatively.

The Arc-Raiders-grounded **VDF→JSM translation work is preserved at `vdf/`** — the user intends to retrace and reapply it in a future project. Treat that subdir as preserved-active: don't delete it, but don't extend it speculatively either. See [`vdf/README.md`](./vdf/README.md) for the load-bearing gotchas.

If the durable hardware facts in `findings/gyro_hid.md` need a companion (e.g. SDL3 driver behavior on Linux), write a fresh finding.

## Current focus

**Linux-side gamepad input on a fresh Arch install.** Diagnosing input latency and gyro availability for the 8BitDo Ultimate 2 Wireless under Steam (native pacman install, Wayland, NVIDIA). Kernel HID driver conflict (`hid-generic` / `xpad` claiming the device before Steam can open `/dev/hidraw*`) is the leading hypothesis.

## Where things go

| Change | Where |
|--------|-------|
| Steps in the current investigation | Edit `8bitdo-ultimate2-arch-linux-troubleshooting.md` directly — it's a living doc |
| New durable hardware/protocol fact | `findings/<topic>.md` |
| New raw artifact (HID dump, log, screenshot) | `reference/<topic>/` (group by source) |
| New Linux diagnostic script | `tools/<name>.py` + line in `tools/README.md` |
| A new investigation that warrants its own doc | New top-level markdown file with descriptive name |
| Material related to the long-term direction (mapper lanes, headless JSM, etc.) | A new top-level markdown file here, citing the canonical spec at `../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md` — but only if it's a deliberate continuation, not speculative drift. Don't fork the spec back into this subdir. |
| VDF→JSM translation tooling or principles | `vdf/` — when reapplying the work in a future project, fork or copy out; don't expand the scope here without intent |

## Conventions

- **No museum-keeping.** When an investigation concludes (resolved or abandoned), promote durable facts into `findings/` and delete the working notes. Don't keep stale handoffs around.
- **The design spec is preserved in the parent tree, not authoritative for current work.** `../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md` captures the most comprehensive past articulation of the long-term direction. Cite its line anchors when referencing concepts; don't mutate it from this lab (it belongs to the parent jangsjyro repo's docs).
- **Real-runtime evidence beats source review.** This is the load-bearing principle from the design spec (`../docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md`, line 197: "Real Steam Input vs real JSM is authoritative"). Apply it locally too: a `man udev` claim or a config-file inspection isn't proof until something fires on the controller.

## Hardware quick-reference

- **Device:** 8BitDo Ultimate 2 Wireless, VID `0x2DC8`, PID `0x6012` (2.4 GHz dongle / D-Input). Other PIDs: `0x310B` USB wired, `0x6013` dongle alone.
- **D-Input activation:** Home + B at power-on.
- **Bluetooth is out of scope** (gyro disabled, 125 Hz polling cap).
- **Firmware:** v1.03+ for the 34-byte sensor-bearing HID report.
