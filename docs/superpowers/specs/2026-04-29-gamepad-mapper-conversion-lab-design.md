# Gamepad Mapper Conversion Lab Design

## Purpose

Build an agent-first lab for converting gamepad mapper configurations between Steam Input and JoyShockMapper (JSM), starting with Steam Input to JSM and preserving a path for JSM to Steam Input later.

The lab exists to measure behavior, not just syntax. Given the same controller input trace, the system compares what real Steam Input emits with what real JSM emits from a candidate converted config. The final product is useful only if generated JSM configs behave closely enough in real JSM, especially on Windows.

## Design Goals

- Convert Steam Input layouts to clean JSM configs, with no explanatory comments in the generated config.
- Preserve bidirectional architecture so JSM to Steam Input can be added later.
- Use real Steam Input and real JSM as the authoritative behavioral oracle.
- Let agents iterate independently through structured artifacts rather than human inspection.
- Track exact, bounded approximation, degraded approximation, unsupported, and requires-user-choice results per feature.
- Record current, previous, and best-known error for each behavior across cycles.
- Support adversarial trace generation to expose failures and improve coverage.
- Persist learned mapper and controller behavior in reference files with evidence links.
- Validate Linux lab results against Windows early, before serious converter work.

## Non-Goals

- Do not rewrite JSM mapping semantics to make tests pass.
- Do not treat headless JSM as the source of truth.
- Do not rely on a single global score to accept conversion changes.
- Do not require touchpad or adaptive trigger support for the first canonical profile.
- Do not make generated JSM configs carry explanation or diagnostics.

## Core Architecture

The lab has two mapper lanes:

- Reference lane: runs the source mapper config.
- Candidate lane: runs the generated target mapper config.

For Steam Input to JSM, Steam Input is the reference and JSM is the candidate. For JSM to Steam Input, the roles are reversed.

Main components:

- Trace runner: emits deterministic virtual controller input.
- Steam Input lane: runs real Steam Input against the trace.
- JSM lane: runs real JSM against the trace.
- Output observer: captures keyboard, mouse, virtual gamepad, motion output, and later haptics/control signals when observable.
- Event normalizer: converts mapper-specific output into canonical typed events.
- Comparator: computes behavior deltas between reference and candidate event streams.
- Converter: generates candidate configs and structured loss reports.
- Knowledge base: stores observed and promoted mapper semantics for future agent work.

Real Steam Input versus real JSM comparison remains authoritative. Headless JSM can accelerate iteration only after parity with real JSM is proven for a feature class.

## Generated Artifacts

Each run should produce structured artifacts that agents can consume without prose interpretation:

- `run.manifest.json`: environment, OS, mapper versions, controller profile, trace suite, source and candidate hashes.
- `reference.events.jsonl`: normalized event stream from the reference mapper.
- `candidate.events.jsonl`: normalized event stream from the candidate mapper.
- `delta.json`: exact/tolerant comparison results and behavior errors.
- `loss.json`: conversion classification and explanation by feature.
- `cycle-history.json`: previous/current/best metrics and stop reasons.
- `report.md`: human summary derived from structured artifacts.
- `candidate.config`: clean generated target config.

The generated target config is runnable output only. Explanations live in reports.

## Result Classifications

Each converted behavior is classified independently:

- `exact`: same behavior within exact-match rules.
- `bounded_approximation`: measurable difference, within useful tolerance.
- `degraded_approximation`: intent preserved but precision, timing, or interaction model is meaningfully worse.
- `unsupported_omitted`: no meaningful target equivalent.
- `requires_user_choice`: multiple plausible translations and no safe default.

Approximations are allowed when they are likely useful to a user and when the system can describe the loss. Approximation quality is judged by trace evidence, not agent confidence.

## Cycle Metrics

Every comparable behavior needs a stable identity and cycle history:

- `feature_id`
- `trace_id`
- `metric`
- `current_error`
- `previous_error`
- `best_error`
- `trend`
- `classification`
- `confidence`
- `stop_reason`

Stop reasons include:

- exact
- under tolerance
- plateaued
- oscillating
- unsupported
- max cycles
- blocked by mapper capability
- blocked by regression risk

This lets agents know whether a degraded behavior is improving, regressing, or pragmatically stuck.

## Validation Policy

Acceptance is conservative and per-feature:

- Real Steam Input vs real JSM is authoritative.
- Headless tests are acceleration only.
- Easy features do not compensate for broken hard features.
- Regressions block acceptance unless explicitly justified.
- Trace suites are versioned.
- Tuning traces and holdout traces are separated.
- Unsupported and degraded behavior must be exposed directly.
- Reports must not hide coverage gaps.

No central scoreboard should determine success. Adversarial search is useful, but score-chasing is not part of the acceptance path.

## Adversarial Trace Generation

Adversarial agents generate traces that expose behavioral differences. They do not define success by themselves.

Trace types:

- Baseline traces for ordinary input.
- Feature-directed traces for activators, layers, chords, gyro, sticks, and triggers.
- Boundary traces around timing windows, deadzones, thresholds, and release order.
- Composition traces combining mode shifts, chords, gyro enable states, and analog movement.
- Mutation traces with small perturbations of timing and axis values.
- Regression traces for previously discovered deltas.
- Holdout traces withheld from converter tuning.

Accepted traces are immutable within a versioned suite. New adversarial traces can reveal failures, but cannot rewrite prior results.

## Controller Profile Strategy

The converter should target mapper-neutral semantic controls, not a single physical controller. The first validation profile should still be concrete and repeatable.

Canonical v1 profile:

- Extended gyro gamepad inspired by 8BitDo Ultimate 2 Wireless.
- Standard face buttons, d-pad, shoulders, stick clicks, start/back/home/capture.
- Analog sticks and triggers.
- Gyro and accelerometer.
- Four extra rear/aux buttons.

Excluded from v1:

- Touchpad finger position.
- Touchpad as a special surface.
- Adaptive trigger force feedback.
- Microphone-button-specific behavior.

Later profiles should check that the converter is not accidentally tied to one device normalization path.

## Platform Strategy

Linux is attractive for automation, but it must prove that its results transfer to Windows. Windows validation happens early.

Rules:

- Linux may become the main automation lab only after early parity gates.
- Windows must certify release confidence for generated JSM configs.
- Platform differences are recorded as platform deltas, not hidden as converter failures.
- JSM Linux changes are allowed only for build, platform glue, test instrumentation, and output/input recording, not mapping semantics.

## Headless JSM

Headless JSM is a test execution mode for JSM, not a reimplementation.

It should:

- Load normal JSM configs through the real parser.
- Replace SDL/JSL device discovery with synthetic controller frames.
- Feed frames into the existing JSM runtime path.
- Replace OS keyboard/mouse output with event recording.
- Replace virtual controller output with event recording.
- Use deterministic trace time where possible.
- Emit normalized JSONL events.

It should share:

- Config parsing.
- Command semantics.
- Button mapping logic.
- Tap, hold, double press, simultaneous press, diagonal press, chord, and modeshift behavior.
- Stick math.
- Gyro math.
- Trigger thresholds.
- Virtual controller mapping decisions.
- Defaults and settings behavior.

It does not prove:

- Steam Input behavior.
- OS-level routing.
- Windows/Linux mouse and scancode quirks.
- SDL device discovery.
- Real controller HID behavior.
- Focus, tray, autoload, and user-session behavior unless explicitly tested.

Existing JSM source already has useful seams:

- `JslWrapper` abstracts input.
- `joyShockPollCallback` is the main input-processing entry point.
- `JoyShock` owns controller processing.
- `DigitalButton` owns button state machines.
- `Gamepad` abstracts virtual controller output.
- `pressKey`, `moveMouse`, and `setMouseNorm` form the keyboard/mouse output boundary.
- The command/setting system already parses JSM config behavior.

Missing pieces include a headless CLI, trace reader, synthetic `JslWrapper`, deterministic time injection, output recorders, and JSONL emission.

## Reference Knowledge Base

The lab should persist learned behavior so agents can answer "what does this control or mapper function do?" without rediscovering it.

Use two knowledge layers:

- `kb/lab-notes/`: agent-written observations linked to evidence. Mutable and noisy.
- `kb/canonical/`: promoted semantics only. Used by converters by default.

Reference files:

- `kb/canonical/control-catalog.json`
- `kb/canonical/mapper-functions.steam.json`
- `kb/canonical/mapper-functions.jsm.json`
- `kb/canonical/equivalence-rules.jsonl`
- `kb/canonical/capability-matrix.json`
- `kb/lab-notes/observations.jsonl`

Each entry must include provenance: run IDs, trace IDs, mapper version, platform, device profile, confidence, and last validation date.

Lab notes may suggest hypotheses. Canonical files guide conversion decisions.

## Human-Readable Phase Plan

### 1. Feasibility Gates

1a. Build and run JSM on Linux with non-semantic changes only.

1b. Run minimal real JSM behavior test on Linux.

1c. Run matching minimal real JSM behavior test on Windows.

1d. Decide whether Linux can be the main automation lab.

### 2. Steam/JSM A-B Proof

2a. Prove Steam Input can be driven by controlled virtual input.

2b. Prove Steam Input output can be observed as typed events.

2c. Run one hand-authored equivalent Steam/JSM mapping.

2d. Compare outputs from both real runtimes.

2e. Repeat or certify the tiny A-B proof on Windows before building expensive general infrastructure.

### 3. Artifact Contracts

3a. Define trace format.

3b. Define normalized event format.

3c. Define delta, loss, and cycle-history formats.

3d. Define run manifest and environment capture.

3e. Define knowledge-base note and promotion formats.

### 4. Real Runtime Harness

4a. Generalize Steam lane.

4b. Generalize JSM lane.

4c. Add output observers.

4d. Add comparator.

4e. Add repeatable run orchestration.

### 5. Headless Acceleration

5a. Add synthetic `JslWrapper`.

5b. Add recording keyboard/mouse output.

5c. Add recording virtual gamepad output.

5d. Add deterministic trace-time control.

5e. Certify headless JSM against real JSM before use.

### 6. Trace Intelligence

6a. Add baseline traces.

6b. Add feature-directed adversarial traces.

6c. Add boundary and mutation traces.

6d. Add regression traces.

6e. Add holdout traces.

### 7. Knowledge Base

7a. Record lab observations from runs.

7b. Promote verified JSM behavior notes.

7c. Promote verified Steam Input behavior notes.

7d. Promote equivalence rules with evidence.

7e. Maintain capability matrix.

### 8. Converter Work

8a. Steam layout parser.

8b. JSM config emitter.

8c. Loss classifier.

8d. Iterative repair loop.

8e. Windows regression suite.

8f. Later: JSM-to-Steam path.

## Open Risks

- Steam Input layout generation and runtime control may be more opaque than JSM config generation.
- Virtual controller shape may be constrained by what Steam Input and JSM reliably recognize.
- Linux automation may not transfer closely enough to Windows for some output channels.
- Mouse deltas, timing, and gyro behavior will need tolerance models.
- Headless JSM may require careful refactoring to avoid accidentally changing runtime behavior.
- Knowledge-base promotion needs strict evidence rules to avoid turning speculation into converter logic.

## Approval State

This design captures the agreed direction: a real-runtime Steam Input vs JSM behavioral lab, agent-first artifacts, early Windows parity gates, adversarial trace generation without score-chasing, a reference knowledge base, and many small isolated tasks grouped into readable phases.
