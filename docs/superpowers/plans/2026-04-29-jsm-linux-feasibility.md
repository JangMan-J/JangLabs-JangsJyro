# JSM Linux Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the first Phase 1a/1b evidence packet showing whether current JSM can build on Linux and whether a minimal real-runtime JSM behavior smoke test can be attempted without semantic mapping changes.

**Architecture:** This is a validator-owned feasibility spike. It records host capabilities, configures and builds the existing CMake project, starts JSM with an isolated `XDG_CONFIG_HOME`, loads a minimal `OnStartup.txt`, and attempts behavior observation only when the host has real Linux input/output access and a controllable controller source.

**Tech Stack:** CMake 3.28+, C++23, Clang, PkgConfig, GTK+3, appindicator3 or compatible package, libevdev/uinput, SDL3 via CMake/CPM, Linux bash.

---

## Scope

This plan covers only Phase 1a and Phase 1b from `docs/superpowers/specs/2026-04-29-gamepad-mapper-conversion-lab-design.md`.

It does not implement Steam Input automation, Windows parity, virtual controller injection, output normalization schemas, headless JSM, or converter logic. It also does not modify JSM source code. If source changes are required to build or run, this plan records the evidence and stops so a smaller follow-up task can be written.

## Run Path Convention

Task 1 generates `RUN_ID` with this exact command:

```sh
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-linux-jsm-feasibility"
```

Every file path containing `$RUN_ID` refers to that generated value. Later tasks recover the concrete path by reading `docs/superpowers/runs/.latest-linux-jsm-feasibility`.

## Files

- Read: `README.md`
- Read: `CMakeLists.txt`
- Read: `cmake/LinuxConfig.cmake`
- Read: `JoyShockMapper/CMakeLists.txt`
- Read: `JoyShockMapper/src/main.cpp`
- Read: `JoyShockMapper/src/linux/InputHelpers.cpp`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/environment.txt`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/source-notes.txt`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/configure.log`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/configure.exitcode`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/build.log`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/build.exitcode`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/binary.txt`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/xdg-config/JoyShockMapper/OnStartup.txt`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/smoke.config`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/runtime.log`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/runtime.exitcode`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/behavior-observation.md`
- Create at execution time: `docs/superpowers/runs/$RUN_ID/result.md`
- Create at execution time: `docs/superpowers/runs/.latest-linux-jsm-feasibility`
- Modify: none expected

## Stop Rules

Stop and write `result.md` instead of improvising when:

- The host is not Linux.
- The host is WSL and the next step requires real runtime input/output access.
- Required dependencies are missing and dependency installation was not explicitly authorized for the execution session.
- CMake configure fails.
- Build fails.
- The JSM binary cannot be located.
- Runtime requires changing shared mapping semantics.
- No controllable controller source exists for pressing `S` and `ZR`.

Allowed outcomes are `pass`, `fail`, and `blocked`. A blocked runtime smoke after a successful build is useful evidence, not a failed plan.

### Task 1: Create Run Directory And Capture Host

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/environment.txt`
- Create: `docs/superpowers/runs/.latest-linux-jsm-feasibility`

- [ ] **Step 1: Create a timestamped run directory**

Run from the repository root on the Linux host:

```sh
mkdir -p docs/superpowers/runs
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-linux-jsm-feasibility"
RUN_DIR="docs/superpowers/runs/$RUN_ID"
mkdir -p "$RUN_DIR"
printf '%s\n' "$RUN_DIR" > docs/superpowers/runs/.latest-linux-jsm-feasibility
printf '%s\n' "$RUN_DIR"
```

Expected: The printed path starts with `docs/superpowers/runs/` and ends with `-linux-jsm-feasibility`.

- [ ] **Step 2: Capture environment facts**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
{
  echo "# Environment"
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "pwd=$(pwd)"
  echo "git_commit=$(git rev-parse HEAD)"
  echo "git_branch=$(git rev-parse --abbrev-ref HEAD)"
  echo "uname=$(uname -a)"
  echo "kernel_name=$(uname -s)"
  if [ -r /proc/version ]; then echo "proc_version=$(cat /proc/version)"; fi
  if [ -r /etc/os-release ]; then echo "os_release_begin"; cat /etc/os-release; echo "os_release_end"; fi
  echo "user=$(id)"
  echo "display=${DISPLAY:-}"
  echo "wayland_display=${WAYLAND_DISPLAY:-}"
  echo "xdg_session_type=${XDG_SESSION_TYPE:-}"
  echo "cmake=$(command -v cmake || true)"
  cmake --version 2>/dev/null | head -n 1 || true
  echo "clang++=$(command -v clang++ || true)"
  clang++ --version 2>/dev/null | head -n 1 || true
  echo "pkg-config=$(command -v pkg-config || true)"
  pkg-config --version 2>/dev/null || true
  for pkg in gtk+-3.0 appindicator3-0.1 ayatana-appindicator3-0.1 libevdev sdl3 SDL3 sdl2 SDL2; do
    printf 'pkg:%s=' "$pkg"
    pkg-config --modversion "$pkg" 2>/dev/null || true
  done
  echo "dev_uinput=$(if [ -e /dev/uinput ]; then ls -l /dev/uinput; else echo missing; fi)"
  echo "dev_input=$(if [ -d /dev/input ]; then ls -ld /dev/input; else echo missing; fi)"
  echo "hidraw_nodes=$(ls /dev/hidraw* 2>/dev/null | tr '\n' ' ')"
  echo "evtest=$(command -v evtest || true)"
  echo "libinput=$(command -v libinput || true)"
  echo "timeout=$(command -v timeout || true)"
} > "$RUN_DIR/environment.txt"
```

Expected: `environment.txt` exists and includes `kernel_name=Linux` when this plan is running on a valid Linux host.

- [ ] **Step 3: Block early on non-Linux hosts**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
if [ "$(uname -s)" != "Linux" ]; then
  {
    echo "# Result"
    echo
    echo "status: blocked"
    echo "reason: this plan must run on a Linux host"
    echo "next: rerun Phase 1a/1b on a real Linux desktop or Linux VM"
  } > "$RUN_DIR/result.md"
  exit 2
fi
```

Expected on Linux: command exits `0` and writes no `result.md`.

Expected outside Linux: command exits `2`, writes `result.md`, and execution stops.

### Task 2: Capture Source Context

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/source-notes.txt`

- [ ] **Step 1: Record the relevant source references**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
{
  echo "# Source Notes"
  echo
  echo "## README Linux build notes"
  sed -n '96,135p' README.md
  echo
  echo "## Root CMake"
  sed -n '1,25p' CMakeLists.txt
  echo
  echo "## Linux dependency CMake"
  sed -n '1,80p' cmake/LinuxConfig.cmake
  echo
  echo "## JSM Linux target sources and SDL linkage"
  sed -n '132,192p' JoyShockMapper/CMakeLists.txt
  echo
  echo "## Linux config folder behavior"
  sed -n '57,105p' JoyShockMapper/src/linux/PlatformDefinitions.cpp
  echo
  echo "## Linux startup argument behavior"
  sed -n '2846,3005p' JoyShockMapper/src/main.cpp
  echo
  echo "## Linux virtual keyboard/mouse output names"
  sed -n '331,360p' JoyShockMapper/src/linux/InputHelpers.cpp
} > "$RUN_DIR/source-notes.txt"
```

Expected: `source-notes.txt` exists and includes `pkg_search_module`, `src/linux/InputHelpers.cpp`, `BASE_JSM_CONFIG_FOLDER`, and `JoyShockMapper_KEYBOARD`.

### Task 3: Configure The Linux Build

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/configure.log`
- Create: `docs/superpowers/runs/$RUN_ID/configure.exitcode`

- [ ] **Step 1: Configure with Clang**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
set -o pipefail
cmake -B build-linux -S . -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang++ 2>&1 | tee "$RUN_DIR/configure.log"
printf '%s\n' "${PIPESTATUS[0]}" > "$RUN_DIR/configure.exitcode"
test "$(cat "$RUN_DIR/configure.exitcode")" = "0"
```

Expected: command exits `0`, `configure.exitcode` contains `0`, and `configure.log` contains CMake configure output.

- [ ] **Step 2: Stop on configure failure**

Run only if Step 1 failed:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
{
  echo "# Result"
  echo
  echo "status: blocked"
  echo "phase: configure"
  echo "configure_exitcode=$(cat "$RUN_DIR/configure.exitcode" 2>/dev/null || echo missing)"
  echo "reason: CMake configure failed; inspect configure.log for missing dependencies or Linux build errors"
  echo "semantic_changes: none"
} > "$RUN_DIR/result.md"
exit 2
```

Expected: `result.md` records a blocked configure result and execution stops.

### Task 4: Build JSM

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/build.log`
- Create: `docs/superpowers/runs/$RUN_ID/build.exitcode`

- [ ] **Step 1: Build the configured target**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
set -o pipefail
cmake --build build-linux 2>&1 | tee "$RUN_DIR/build.log"
printf '%s\n' "${PIPESTATUS[0]}" > "$RUN_DIR/build.exitcode"
test "$(cat "$RUN_DIR/build.exitcode")" = "0"
```

Expected: command exits `0`, `build.exitcode` contains `0`, and `build.log` contains compiler/linker output.

- [ ] **Step 2: Stop on build failure**

Run only if Step 1 failed:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
{
  echo "# Result"
  echo
  echo "status: blocked"
  echo "phase: build"
  echo "configure_exitcode=$(cat "$RUN_DIR/configure.exitcode" 2>/dev/null || echo missing)"
  echo "build_exitcode=$(cat "$RUN_DIR/build.exitcode" 2>/dev/null || echo missing)"
  echo "reason: build failed; inspect build.log before proposing any non-semantic Linux build fix"
  echo "semantic_changes: none"
} > "$RUN_DIR/result.md"
exit 2
```

Expected: `result.md` records a blocked build result and execution stops.

### Task 5: Locate Binary And Prepare Isolated Config

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/binary.txt`
- Create: `docs/superpowers/runs/$RUN_ID/xdg-config/JoyShockMapper/OnStartup.txt`
- Create: `docs/superpowers/runs/$RUN_ID/smoke.config`

- [ ] **Step 1: Locate the built JSM binary**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
if [ -x build-linux/JoyShockMapper/JoyShockMapper ]; then
  BINARY="build-linux/JoyShockMapper/JoyShockMapper"
else
  BINARY="$(find build-linux -maxdepth 5 -type f -name JoyShockMapper -perm -111 | head -n 1)"
fi
printf '%s\n' "$BINARY" > "$RUN_DIR/binary.txt"
test -n "$BINARY"
test -x "$BINARY"
```

Expected: `binary.txt` contains an executable path.

- [ ] **Step 2: Stop if the binary cannot be found**

Run only if Step 1 failed:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
{
  echo "# Result"
  echo
  echo "status: blocked"
  echo "phase: binary"
  echo "reason: build completed but no executable JoyShockMapper binary was found under build-linux"
  echo "semantic_changes: none"
} > "$RUN_DIR/result.md"
exit 2
```

Expected: `result.md` records a blocked binary-location result and execution stops.

- [ ] **Step 3: Create the isolated startup config**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
mkdir -p "$RUN_DIR/xdg-config/JoyShockMapper"
cat > "$RUN_DIR/xdg-config/JoyShockMapper/OnStartup.txt" <<'EOF'
RESET_MAPPINGS
S = SPACE
ZR = LMOUSE
EOF
cp "$RUN_DIR/xdg-config/JoyShockMapper/OnStartup.txt" "$RUN_DIR/smoke.config"
```

Expected: both config files contain exactly:

```text
RESET_MAPPINGS
S = SPACE
ZR = LMOUSE
```

### Task 6: Start Real JSM With The Smoke Config

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/runtime.log`
- Create: `docs/superpowers/runs/$RUN_ID/runtime.exitcode`

- [ ] **Step 1: Run JSM long enough to load the isolated config**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
BINARY="$(cat "$RUN_DIR/binary.txt")"
set -o pipefail
XDG_CONFIG_HOME="$RUN_DIR/xdg-config" timeout 8s "$BINARY" 2>&1 | tee "$RUN_DIR/runtime.log"
STATUS="${PIPESTATUS[0]}"
printf '%s\n' "$STATUS" > "$RUN_DIR/runtime.exitcode"
test "$STATUS" = "0" || test "$STATUS" = "124"
```

Expected: exit code is `0` or `124`. Exit code `124` means `timeout` stopped JSM after the smoke window, which is acceptable for this process-start check.

- [ ] **Step 2: Check whether JSM loaded the smoke config**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
grep -E "Loading commands from file|Finished executing startup file|Welcome to JoyShockMapper" "$RUN_DIR/runtime.log" > "$RUN_DIR/runtime-summary.txt"
grep -q "Welcome to JoyShockMapper" "$RUN_DIR/runtime.log"
grep -q "Finished executing startup file" "$RUN_DIR/runtime.log"
```

Expected: `runtime-summary.txt` exists, JSM prints its welcome line, and `runtime.log` shows the startup file completed.

- [ ] **Step 3: Stop if JSM cannot start or load the config**

Run only if Step 1 or Step 2 failed:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
{
  echo "# Result"
  echo
  echo "status: blocked"
  echo "phase: runtime-start"
  echo "runtime_exitcode=$(cat "$RUN_DIR/runtime.exitcode" 2>/dev/null || echo missing)"
  echo "reason: JSM did not start cleanly or did not load the isolated OnStartup.txt"
  echo "semantic_changes: none"
} > "$RUN_DIR/result.md"
exit 2
```

Expected: `result.md` records a blocked runtime-start result and execution stops.

### Task 7: Attempt Minimal Behavior Observation

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/behavior-observation.md`

- [ ] **Step 1: Classify whether behavior observation is possible on this host**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
IS_WSL=no
if [ -r /proc/version ] && grep -qi microsoft /proc/version; then IS_WSL=yes; fi
HAS_UINPUT=no
if [ -e /dev/uinput ] && [ -w /dev/uinput ]; then HAS_UINPUT=yes; fi
HAS_INPUT_DIR=no
if [ -d /dev/input ] && [ -r /dev/input ]; then HAS_INPUT_DIR=yes; fi
HAS_EVENT_OBSERVER=no
if command -v evtest >/dev/null 2>&1 || command -v libinput >/dev/null 2>&1; then HAS_EVENT_OBSERVER=yes; fi
HAS_CONTROLLER_SOURCE=no
if ls /dev/input/js* >/dev/null 2>&1 || ls /dev/input/by-id/*joystick* >/dev/null 2>&1 || ls /dev/hidraw* >/dev/null 2>&1; then HAS_CONTROLLER_SOURCE=yes; fi
{
  echo "# Behavior Observation"
  echo
  echo "is_wsl=$IS_WSL"
  echo "has_uinput_write=$HAS_UINPUT"
  echo "has_input_dir=$HAS_INPUT_DIR"
  echo "has_event_observer=$HAS_EVENT_OBSERVER"
  echo "has_controller_source=$HAS_CONTROLLER_SOURCE"
  echo
  echo "required_behavior:"
  echo "- Press/release JSM input S and observe SPACE down/up from JoyShockMapper_KEYBOARD."
  echo "- Press/release JSM input ZR and observe BTN_LEFT down/up from JoyShockMapper_MOUSE."
} > "$RUN_DIR/behavior-observation.md"
```

Expected: `behavior-observation.md` records host capability flags.

- [ ] **Step 2: Record blocked behavior observation when prerequisites are missing**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
if grep -q 'is_wsl=yes' "$RUN_DIR/behavior-observation.md" ||
   grep -q 'has_uinput_write=no' "$RUN_DIR/behavior-observation.md" ||
   grep -q 'has_input_dir=no' "$RUN_DIR/behavior-observation.md" ||
   grep -q 'has_event_observer=no' "$RUN_DIR/behavior-observation.md" ||
   grep -q 'has_controller_source=no' "$RUN_DIR/behavior-observation.md"; then
  cat >> "$RUN_DIR/behavior-observation.md" <<'EOF'

observation_status: blocked
reason: host lacks one or more prerequisites for autonomous real-runtime input/output observation
accepted_as_phase_1b_result: yes, because this feasibility spike must report host limits instead of inventing a tester
EOF
else
  cat >> "$RUN_DIR/behavior-observation.md" <<'EOF'

observation_status: ready_for_real_runtime_attempt
reason: host appears to have uinput, input nodes, an event observer, and at least one possible controller source
EOF
fi
```

Expected: `behavior-observation.md` includes either `observation_status: blocked` or `observation_status: ready_for_real_runtime_attempt`.

- [ ] **Step 3: Attempt the real-runtime behavior test only when ready**

Run only if `behavior-observation.md` contains `observation_status: ready_for_real_runtime_attempt`:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
cat >> "$RUN_DIR/behavior-observation.md" <<'EOF'

manual_or_external_input_required:
- The repository does not yet contain the virtual controller trace runner.
- Do not fake the S/ZR input result.
- If an execution environment provides a controllable real or virtual controller, record the exact command/tool used here before marking pass.

expected_events:
- JoyShockMapper_KEYBOARD emits KEY_SPACE value 1 then KEY_SPACE value 0 after S press/release.
- JoyShockMapper_MOUSE emits BTN_LEFT value 1 then BTN_LEFT value 0 after ZR press/release.
EOF
```

Expected: The file explicitly states that a controllable input source is required and that results must not be faked.

### Task 8: Write Final Result

**Files:**
- Create: `docs/superpowers/runs/$RUN_ID/result.md`

- [ ] **Step 1: Write the final result summary**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
CONFIGURE_EXIT="$(cat "$RUN_DIR/configure.exitcode" 2>/dev/null || echo missing)"
BUILD_EXIT="$(cat "$RUN_DIR/build.exitcode" 2>/dev/null || echo missing)"
RUNTIME_EXIT="$(cat "$RUN_DIR/runtime.exitcode" 2>/dev/null || echo missing)"
BINARY="$(cat "$RUN_DIR/binary.txt" 2>/dev/null || echo missing)"
OBS_STATUS="$(grep '^observation_status:' "$RUN_DIR/behavior-observation.md" 2>/dev/null | head -n 1 | cut -d: -f2- | xargs || echo missing)"
if [ "$CONFIGURE_EXIT" = "0" ] && [ "$BUILD_EXIT" = "0" ] && [ "$BINARY" != "missing" ] && [ "$OBS_STATUS" = "blocked" ]; then
  STATUS="blocked"
  REASON="JSM built and launched, but autonomous behavior observation was blocked by host/runtime prerequisites"
elif [ "$CONFIGURE_EXIT" = "0" ] && [ "$BUILD_EXIT" = "0" ] && [ "$BINARY" != "missing" ] && [ "$OBS_STATUS" = "ready_for_real_runtime_attempt" ]; then
  STATUS="blocked"
  REASON="JSM built and launched, and host appears ready, but the repository still lacks an autonomous controller trace runner for S/ZR"
else
  STATUS="blocked"
  REASON="one or more earlier feasibility steps did not complete"
fi
{
  echo "# JSM Linux Feasibility Result"
  echo
  echo "status: $STATUS"
  echo "reason: $REASON"
  echo "configure_exitcode: $CONFIGURE_EXIT"
  echo "build_exitcode: $BUILD_EXIT"
  echo "runtime_exitcode: $RUNTIME_EXIT"
  echo "binary: $BINARY"
  echo "behavior_observation: $OBS_STATUS"
  echo "semantic_changes: none"
  echo
  echo "artifacts:"
  echo "- environment.txt"
  echo "- source-notes.txt"
  echo "- configure.log"
  echo "- build.log"
  echo "- binary.txt"
  echo "- smoke.config"
  echo "- runtime.log"
  echo "- behavior-observation.md"
  echo
  echo "next:"
  echo "- If configure or build failed, write a smaller non-semantic Linux build-fix task."
  echo "- If build and launch passed but behavior observation was blocked, write the virtual controller trace-runner feasibility task."
  echo "- Do not begin Steam Input work until Phase 1c Windows JSM smoke parity is planned."
} > "$RUN_DIR/result.md"
```

Expected: `result.md` exists and names the exact next task class.

- [ ] **Step 2: Review the artifact set**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
find "$RUN_DIR" -maxdepth 3 -type f | sort
```

Expected: the output lists at least `environment.txt`, `source-notes.txt`, `configure.log`, `build.log`, `binary.txt`, `smoke.config`, `runtime.log`, `behavior-observation.md`, and `result.md`.

### Task 9: Commit The Evidence Packet

**Files:**
- Commit: `docs/superpowers/runs/$RUN_ID/environment.txt`
- Commit: `docs/superpowers/runs/$RUN_ID/source-notes.txt`
- Commit: `docs/superpowers/runs/$RUN_ID/configure.log`
- Commit: `docs/superpowers/runs/$RUN_ID/configure.exitcode`
- Commit: `docs/superpowers/runs/$RUN_ID/build.log`
- Commit: `docs/superpowers/runs/$RUN_ID/build.exitcode`
- Commit: `docs/superpowers/runs/$RUN_ID/binary.txt`
- Commit: `docs/superpowers/runs/$RUN_ID/smoke.config`
- Commit: `docs/superpowers/runs/$RUN_ID/runtime.log`
- Commit: `docs/superpowers/runs/$RUN_ID/runtime.exitcode`
- Commit: `docs/superpowers/runs/$RUN_ID/behavior-observation.md`
- Commit: `docs/superpowers/runs/$RUN_ID/result.md`

- [ ] **Step 1: Stage only the evidence packet**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
git add "$RUN_DIR/environment.txt" \
        "$RUN_DIR/source-notes.txt" \
        "$RUN_DIR/configure.log" \
        "$RUN_DIR/configure.exitcode" \
        "$RUN_DIR/build.log" \
        "$RUN_DIR/build.exitcode" \
        "$RUN_DIR/binary.txt" \
        "$RUN_DIR/smoke.config" \
        "$RUN_DIR/runtime.log" \
        "$RUN_DIR/runtime.exitcode" \
        "$RUN_DIR/behavior-observation.md" \
        "$RUN_DIR/result.md"
```

Expected: only the current run evidence files are staged.

- [ ] **Step 2: Commit the evidence packet**

Run:

```sh
RUN_DIR="$(cat docs/superpowers/runs/.latest-linux-jsm-feasibility)"
git commit -m "Record JSM Linux feasibility evidence"
```

Expected: a commit is created. If there is nothing to commit because execution stopped before artifacts were created, do not force an empty commit; report the blocker instead.

## Self-Review Checklist

- This plan has one owner role: Validator agent.
- This plan does not ask an agent to change JSM source code.
- This plan records WSL as build-only unless runtime access is explicitly available and accepted.
- This plan avoids fake controller behavior results.
- This plan stores artifacts under `docs/superpowers/runs/`.
- This plan creates a concrete `OnStartup.txt` smoke config without relying on Linux CLI argument handling.
- This plan stops before Steam Input, Windows parity, headless JSM, and converter work.
