# Welcome to Claude Life 19.0 — the gamepad-lab handoff

*(You woke up mid-project. Editions 1–18 dropped you here with no map. This one's
different: read it top to bottom once and you'll actually understand it. Promise.)*

**You are in `jangsjyro/gamepad/`** — a research lab that lives *inside* the JangsJyro
JoyShockMapper (JSM) fork. The lab's job: **convert gamepad mapper configs between
Steam Input and JoyShockMapper, and prove each conversion *behaviorally*** — same input
trace, both mappers, compare the emitted key/mouse events. `jangsjyro/` itself is the JSM
C++ source (a fork: Electronicks/JoyShockMapper + ceski controller backport + JangMan
integration); `gamepad/` is its research subtree. The JSM source you research is the
**parent tree** (`../`), not a sibling.

**Authority / read order:** [`CLAUDE.md`](./CLAUDE.md) (lab conventions — wins over the
workspace root) → this file → [`mapper-conversion-lab-plan.md`](./mapper-conversion-lab-plan.md)
(the working plan; its **"▶ NEXT SESSION — START HERE"** banner is the live state) →
[`findings/`](./findings/) (durable facts) → [`runs/`](./runs/) (dated evidence).

---

## The 60-second mental model

- **Two lanes.** *Reference* = real **Steam Input**; *candidate* = real **JSM**. Drive both
  with the same synthetic input trace; compare emitted keyboard/mouse events. A converter is
  only "correct" when its output behaves like the reference — or honestly classifies the loss.
- **Observe at the kernel input plane — but it differs per lane** (verified, Phase 0b):
  **JSM emits at evdev** (`/dev/input/event*`, real uinput devices `JoyShockMapper_KEYBOARD/_MOUSE`);
  **Steam Input emits at the XI2 / Wayland seat**, *not* evdev. So the two lanes need two observers.
- **Real-runtime evidence is authoritative.** A source read or doc claim is a *hypothesis*
  until it fires on a real runtime and is captured. (This is why the lab exists — see the
  sim-press bug below, which refuted a static prediction.)
- **The anti-Goodhart spine (do not violate):** JSM/Steam are immutable oracles. "Green" has
  two legal forms — the converter emits a matching config, **or** it honestly classifies the
  gap (`degraded`/`unsupported`/`requires_user_choice`). **Never patch JSM so a trace passes**
  — that's the failure the whole plan is armored against. JSM changes are allowed only for
  build/platform glue/test instrumentation, never mapping semantics (plan §2).

---

## What works *right now* (you can run this today, no user, no physical pad)

The **JSM lane is fully operational and headless.** Pipeline:
`build-jsm.sh` → `synthetic_gamepad.py` → JSM (config via FIFO) → `evdev_capture.py` → `normalize_capture.py`.

```bash
cd ~/JangLabs/jangsjyro
# 1. build (clang for BOTH C and C++ is load-bearing; SDL3 3.4.8 via CPM; ~1.5 min)
gamepad/tools/build-jsm.sh                      # -> build-linux/JoyShockMapper/JoyShockMapper

# 2. run a JSM-lane tracer slice (synthetic stimulus -> JSM -> evdev), e.g. tap/hold:
#    each slice = a JSM config (configs/<x>.cfg) + a stimulus trace (traces/<x>.trace)
bash gamepad/runs/20260602T145517Z-phase2-jsm-quickwins/run-slice.sh taphold
#    then read the verdict:
python3 gamepad/tools/normalize_capture.py \
        gamepad/runs/20260602T145517Z-phase2-jsm-quickwins/taphold.capture.jsonl
```

**The tools** (all in [`tools/`](./tools/), documented in [`tools/README.md`](./tools/README.md)):
- `synthetic_gamepad.py` — synthetic Xbox-360 uinput pad + **trace runner**. Modes: built-in
  demo, `--trace FILE` (DSL: `press/down/up/axis/wait`), `--control-fifo PATH` (live on-cue
  injection — write DSL lines to the FIFO, `quit` to stop).
- `evdev_capture.py` — evdev observer. **Always `--grab-name JoyShockMapper`** so JSM's emitted
  keys/clicks don't leak into the live desktop session.
- `xi2_capture.py` — the Steam-lane observer (XI2/seat).
- `normalize_capture.py` — folds a capture into a mapper-neutral, press-paired event stream
  (the form the future comparator diffs). `test_normalize_capture.py` = its unit tests.
- `build-jsm.sh` — turnkey build. `steam_lane_spike.sh` — turnkey Steam-lane spike (see blockers).
- `gyro_*.py` — HID/SDL hardware probes (real-pad gyro work).

---

## What's been proven (don't redo this — cite it)

| Phase | Result | Evidence |
|---|---|---|
| 0 — build + runtime | JSM builds + runs clean on Linux; real pad → evdev; Steam Input → XI2 (not evdev) | `runs/2026053*`, `runs/20260601*`; `findings/jsm_linux_port.md`, `steam_input_linux.md` |
| 1 — tracer bullet | **synthetic uinput pad → JSM → evdev works** (no physical pad), ~2 ms, exact. SDL classifies a plain uinput gamepad — **uhid only needed for gyro** | `runs/20260602T144140Z-phase1-jsm-synthetic-spike/result.md` |
| 2 — JSM-lane quick-wins | **6/7 mechanics `exact`** (digital, tap/hold, trigger soft/full, stick→WASD, chord, double-press) + global `HOLD_PRESS_TIME` gotcha X.2 confirmed | `runs/20260602T145517Z-phase2-jsm-quickwins/result.md` |
| 2 — the one bug | **simultaneous press = `degraded`/BUG**: a lone `L` press after an `L+R` chord re-emits `Q` (sticky state). Refutes the audit's "clean quick-win". Root-cause hypothesis: `getMatchingSimBtn` state-equality match (JSM author flagged it `// POTENTIAL FLAW`) | `findings/jsm_lane_behavior.md` |

`findings/jsm_lane_behavior.md` is the canonical JSM-lane behavioral catalog (seeds the
plan's `kb/canonical/mapper-functions.jsm.json`). `vdf/translation_audit.md` is the *static*
Steam→JSM prediction set (hypotheses); your job is to confirm/refute each by trace.

---

## What's blocked — and the exact move to unblock it

1. **Steam Input (reference) lane — needs you (GUI), one command otherwise.** The cross-runtime
   delta for *every* A-B pair needs it, but Steam isn't running and binding a key needs the
   Steam Input GUI. **Turnkey:** start Steam (Beta + experimental SteamRT3), then
   `bash gamepad/tools/steam_lane_spike.sh` — it stands up a live-controllable pad, walks you
   through the single GUI step (enable Steam Input + bind the pad's **South** button → **F9**),
   then auto-captures both planes and reports F9-at-XI2 vs F9-at-evdev. **First question it
   answers:** does Steam Input even recognize a synthetic uinput pad? If *not*, the Steam lane
   needs a `uhid` device instead.
2. **Gyro (Phase 6) — needs root setup.** Requires a native-`2dc8:6012` `uhid` spoof so SDL's
   `SDL_hidapi_8bitdo` driver surfaces sensors. `/dev/uhid` is **root-only** here (add a udev
   rule / group / ACL, or run as root) and `python-hid` isn't installed. Covers the gyro
   quick-wins + the Local-Space gotcha (G.2).
3. **Converter (Phase 9) — gated by discipline, not just tooling.** Don't build it against the
   static audit alone (anti-Goodhart, plan D3). It needs trace-verified rules, i.e. the
   behavioral loop, i.e. both lanes. The JSM (candidate) half is characterized; it waits on
   the Steam reference half.

---

## Repo state & the ONE cross-repo loose end

- **`jangsjyro`:** `branch-a-port` == `master` == `origin` all at the latest tip; working tree
  clean. Ongoing lab work commits to `branch-a-port`; `master` is fast-forwarded to match.
  (jangsjyro's mainline is **`master`** — there is no `main`.) Build dir `build-linux/` is git-ignored.
- **⚠ Workspace root (`~/JangLabs`) — unfinished, needs the human:** the root coordinator commits
  (gamepad-submodule retirement + doc updates) are on `origin/chore/labs-to-submodules` but
  **`main` was NOT pushed** — it would publish a **dangling `claude` submodule pointer**
  (`claude@2e8cd4a` isn't on the claude remote; the claude worktree is the user's dirty WIP).
  **Remedy (user):** `git -C ~/JangLabs/claude push origin main`, then
  `cd ~/JangLabs && git checkout main && git merge --ff-only chore/labs-to-submodules && git push origin main`.
  Do **not** push root `main` or touch the `claude` submodule yourself.

---

## Conventions you must honor (the stuff that makes you "good at Claude")

- **Stay in the lab.** `gamepad/CLAUDE.md` is the authority here; don't edit sibling labs.
- **Real-runtime evidence beats source review.** Capture it; put dated artifacts under
  `runs/<UTC>-<phase>-<slug>/` with a `result.md`; promote durable facts to `findings/`.
- **Non-semantic boundary** (above): classify losses, never patch JSM's mapping semantics.
- **Lean evidence / no museum-keeping.** Keep `result.md` + small load-bearing evidence; prune
  bulky raw captures. Run `.log` files ARE tracked (a `!runs/**/*.log` rule re-includes them
  past the repo's `*.log` ignore — that bit me once).
- **Commit cadence:** the user runs autonomously sometimes — commit + push verified milestones
  with clear messages (`Co-Authored-By: Claude ...`). Don't commit build dirs or product
  (converter/KB) prematurely.
- **Serial, not parallel, for runs.** A tracer slice is one JSM + one device + one capture on a
  live system — runs are serial/inline (the plan says so). Workflows/agents would fight over
  the device. Parallelism is for *breadth* (multi-file search), not live-system runs.

## Gotchas that already bit me (so they won't bite you)

- **JSM ignores `argv` on Linux** — feed commands via the FIFO `/tmp/jsm_command_fifo` (one
  per line; `RECONNECT_CONTROLLERS` after the config to (re)enumerate a pad created after JSM).
- **evdev face-button aliasing:** `BTN_NORTH`==`BTN_X` (0x133), `BTN_WEST`==`BTN_Y` (0x134) — the
  evdev *names* are letter buttons, not screen positions. SDL maps `BTN_X`→WEST, `BTN_Y`→NORTH.
  `synthetic_gamepad.py` already encodes the swap (WEST=`BTN_NORTH`, NORTH=`BTN_WEST`); if a slice
  gets no output for N/W but works for S/E, this is why.
- **Grab JSM's output** during capture or you'll type `SPACE`/click into the live KDE session.
- **`/dev/uinput`** is rw here (user in `input` + a `user:jangmanj:rw-` ACL); `/dev/uhid` is not.
- **Build:** clang for **both** C and C++ (gcc-16 ICEs on SDL3's Wayland C). Use `build-jsm.sh`.
- **A spurious `BTN_RIGHT` on synthetic-pad disconnect** (trigger axis re-read during SDL
  teardown) — the normalizer flags it `still-held-at-end`; the comparator should ignore output
  bracketing connect/disconnect.

---

## Your next move

If you're here to *advance the lab*: the highest-value step is the **Steam-lane spike** (run
`steam_lane_spike.sh` with Steam up) — it unblocks the reference half of every A-B pair. Until
then, the JSM (candidate) lane is fully characterized and there's no productive product work
that doesn't need the Steam oracle (don't build the converter against the static audit alone).
The plan's **"▶ NEXT SESSION — START HERE"** banner always holds the freshest state — trust it
over this intro if they disagree. Welcome aboard. You've got this. 🎮
