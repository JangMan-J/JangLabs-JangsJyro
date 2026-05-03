# Requirements Document: JyroPort

## Introduction

JyroPort is an agent-first behavioral conversion lab for gamepad mapper configurations. The system converts configurations between Steam Input and JoyShockMapper (JSM) by comparing real runtime behavior rather than performing syntactic translation. The lab measures behavioral equivalence through deterministic trace execution, captures and normalizes output events, computes deltas between reference and candidate mappers, and iteratively improves conversion quality through structured artifacts and an evidence-backed knowledge base.

The system supports exact matches, bounded approximations, degraded approximations, explicitly unsupported features, and user-choice scenarios, with cycle-by-cycle tracking of improvement, regression, or plateau states.

## Glossary

- **Trace**: A deterministic sequence of virtual controller input frames with microsecond timestamps
- **Mapper**: A gamepad configuration system (Steam Input or JoyShockMapper)
- **Reference_Lane**: The source mapper whose behavior is being replicated (typically Steam Input)
- **Candidate_Lane**: The target mapper whose configuration is being generated (typically JSM)
- **Frame**: A single timestamped snapshot of controller state (buttons, axes, gyro, accel)
- **Output_Observer**: Component that captures keyboard, mouse, gamepad, and motion output from mappers
- **Event_Normalizer**: Component that converts mapper-specific output into canonical typed events
- **Comparator**: Component that computes behavioral deltas between reference and candidate event streams
- **Delta**: Structured representation of differences between reference and candidate outputs
- **Loss_Report**: Classification of conversion quality per feature with evidence and explanations
- **Converter**: Component that generates candidate configs and repairs them based on loss reports
- **Knowledge_Base**: Evidence-backed repository of mapper semantics and equivalence rules
- **Lab_Notes**: Unverified observations from runs awaiting promotion to canonical knowledge
- **Cycle_History**: Record of error metrics, trends, and classifications across converter iterations
- **Trace_Suite**: Versioned collection of traces with access levels (tuning, regression, holdout)
- **Run_Manifest**: Metadata document describing environment, versions, artifacts for a single run
- **Headless_JSM**: Synthetic JSM runtime with deterministic input injection for faster iteration
- **Platform_Delta_Catalog**: Record of known behavioral differences between Linux and Windows

## Requirements

### Requirement 1: Trace Execution

**User Story:** As a conversion lab operator, I want to execute deterministic controller input traces against both mappers simultaneously, so that I can compare their behavioral outputs under identical conditions.

#### Acceptance Criteria

1. WHEN a valid trace file is provided, THE Trace_Runner SHALL parse it into a Trace object with version, profile, frames, and metadata
2. WHEN executing a trace, THE Trace_Runner SHALL emit virtual controller input to multiple Mapper targets simultaneously
3. WHEN emitting frames, THE Trace_Runner SHALL maintain microsecond timestamp precision
4. WHEN executing a trace, THE Trace_Runner SHALL maintain frame-accurate synchronization across all targets

### Requirement 2: Output Capture

**User Story:** As a conversion lab operator, I want to capture all observable output from both mappers, so that I can compare their behavioral responses.

#### Acceptance Criteria

1. WHEN a mapper produces keyboard output, THE Output_Observer SHALL capture scancodes, keycodes, key names, and state (down/up) with microsecond timestamps
2. WHEN a mapper produces keyboard output, THE Output_Observer SHALL isolate capture per mapper target to prevent cross-contamination
3. WHEN a mapper produces mouse output, THE Output_Observer SHALL capture button events, movement deltas, and wheel events with microsecond timestamps
4. WHEN a mapper produces virtual gamepad output, THE Output_Observer SHALL capture button state and axis values with microsecond timestamps
5. WHEN a mapper produces motion output, THE Output_Observer SHALL capture motion events when observable
6. WHEN capture completes, THE Output_Observer SHALL return all captured events grouped by type (keyboard, mouse, virtualGamepad, motion)

### Requirement 3: Event Normalization

**User Story:** As a conversion lab operator, I want mapper-specific output converted into canonical typed events, so that I can compare outputs from different mappers.

#### Acceptance Criteria

1. WHEN normalizing keyboard events, THE Event_Normalizer SHALL map platform-specific scancodes to canonical key names
2. WHEN normalizing mouse events, THE Event_Normalizer SHALL convert button numbers, movement deltas, and wheel deltas to canonical format
3. WHEN normalizing gamepad events, THE Event_Normalizer SHALL convert button and axis identifiers to canonical names
4. WHEN normalizing any event, THE Event_Normalizer SHALL preserve microsecond timestamp precision
5. WHEN normalization completes, THE Event_Normalizer SHALL validate output against the normalized event schema
6. WHEN normalization completes, THE Event_Normalizer SHALL tag each event with its mapper source

### Requirement 4: Behavioral Comparison

**User Story:** As a conversion lab operator, I want to compute structured deltas between reference and candidate event streams, so that I can measure conversion quality.

#### Acceptance Criteria

1. WHEN comparing event streams, THE Comparator SHALL identify exact matches where events are identical
2. WHEN comparing event streams, THE Comparator SHALL identify tolerant matches where events differ within configured timing or value tolerances
3. WHEN comparing event streams, THE Comparator SHALL identify missing events present in reference but absent in candidate
4. WHEN comparing event streams, THE Comparator SHALL identify extra events present in candidate but absent in reference
5. WHEN comparing event streams, THE Comparator SHALL compute timing deltas for matched events
6. WHEN comparing event streams, THE Comparator SHALL compute value deltas for analog events
7. WHEN comparing event streams, THE Comparator SHALL detect sequence order violations
8. WHEN comparison completes, THE Comparator SHALL output a Delta object with exact, tolerant, missing, extra, timing, value, and sequence fields
9. WHEN classifying a delta for a feature, THE Comparator SHALL assign one of: exact, bounded_approximation, degraded_approximation, unsupported_omitted, or requires_user_choice

### Requirement 5: Configuration Conversion

**User Story:** As a conversion lab operator, I want to generate candidate JSM configs from Steam Input layouts and iteratively repair them based on loss reports, so that I can achieve behavioral equivalence.

#### Acceptance Criteria

1. WHEN converting a source config, THE Converter SHALL parse the source mapper configuration format
2. WHEN converting a source config, THE Converter SHALL query the Knowledge_Base for control semantics, mapper function semantics, and equivalence rules
3. WHEN generating a candidate config, THE Converter SHALL emit syntactically valid target mapper configuration files
4. WHEN generating a loss report, THE Converter SHALL classify each feature as exact, bounded_approximation, degraded_approximation, unsupported_omitted, or requires_user_choice
5. WHEN generating a loss report, THE Converter SHALL provide explanations with evidence links for each feature classification
6. WHEN repairing a candidate config, THE Converter SHALL update conversion rules based on the previous cycle's loss report
7. WHEN tracking conversion cycles, THE Converter SHALL record error metrics, trends (new, improved, regressed, unchanged, incomparable), and confidence per feature
8. WHEN a stop condition is met, THE Converter SHALL set stop reason to one of: exact, under_tolerance, plateaued, oscillating, unsupported, max_cycles, blocked_by_mapper_capability, or blocked_by_regression_risk

### Requirement 6: Knowledge Base

**User Story:** As a conversion lab operator, I want to build an evidence-backed knowledge base of mapper semantics, so that the converter can make informed decisions based on verified runtime behavior.

#### Acceptance Criteria

1. WHEN querying control semantics, THE Knowledge_Base SHALL return control type, neutral value, range, unit, and provenance
2. WHEN querying mapper function semantics, THE Knowledge_Base SHALL return syntax, behavior description, parameters, constraints, and provenance
3. WHEN querying equivalence rules, THE Knowledge_Base SHALL return source function, target function, classification, conditions, evidence links, and last validated date
4. WHEN querying capabilities, THE Knowledge_Base SHALL return a capability matrix showing which features are supported, approximated, or unsupported per mapper
5. WHEN recording observations, THE Lab_Notes SHALL link observations to evidence (run ID, trace ID, delta, loss report)
6. WHEN promoting lab notes to canonical knowledge, THE Knowledge_Base SHALL require at least one real-runtime evidence link with validation
7. WHEN a new observation contradicts existing canonical knowledge, THE Lab_Notes SHALL append the observation with a conflict marker without overwriting canonical entries

### Requirement 7: Run Orchestration

**User Story:** As a conversion lab operator, I want automated orchestration of trace execution, output capture, normalization, comparison, and artifact generation, so that I can run repeatable experiments.

#### Acceptance Criteria

1. WHEN starting a run, THE Run_Orchestrator SHALL generate a unique run ID (UUID)
2. WHEN starting a run, THE Run_Orchestrator SHALL capture environment metadata (OS, OS version, kernel, architecture, hostname, user)
3. WHEN starting a run, THE Run_Orchestrator SHALL record mapper versions (type, version, commit, build config) for both reference and candidate
4. WHEN starting a run, THE Run_Orchestrator SHALL record controller profile and trace suite reference
5. WHEN starting a run, THE Run_Orchestrator SHALL compute SHA-256 hashes of source and candidate configs
6. WHEN a run completes, THE Run_Orchestrator SHALL write a run manifest with run ID, timestamp, environment, mappers, controller, trace suite, hashes, and artifact paths
7. WHEN a run completes, THE Run_Orchestrator SHALL write reference events to a file validated against the normalized event schema
8. WHEN a run completes, THE Run_Orchestrator SHALL write candidate events to a file validated against the normalized event schema
9. WHEN a run completes, THE Run_Orchestrator SHALL write delta to a file validated against the delta schema
10. WHEN a run completes, THE Run_Orchestrator SHALL write loss report to a file validated against the loss report schema
11. WHEN a run completes, THE Run_Orchestrator SHALL generate a human-readable summary report from structured artifacts

### Requirement 8: Trace Suite Management

**User Story:** As a conversion lab operator, I want to manage versioned trace suites with access levels, so that I can control which traces are visible to converter agents.

#### Acceptance Criteria

1. WHEN creating a trace suite, THE Trace_Suite SHALL include suite ID, version, traces, targeted features, access level, and intent
2. WHEN adding a trace to a suite, THE Trace_Suite SHALL record trace ID, path, SHA-256 hash, targeted features, and intent
3. WHEN versioning a trace suite, THE Trace_Suite SHALL make all traces within that version immutable
4. WHEN a trace has access level 'holdout', THE Trace_Suite SHALL prevent converter agents from accessing trace contents
5. WHEN creating trace metadata, THE Trace_Suite SHALL include trace ID, version, created timestamp, profile, duration, frame count, targeted features, and intent
6. WHEN creating a trace, THE Trace_Suite SHALL include an intent field explaining what behavioral difference the trace exposes
7. WHEN a converter agent queries traces, THE Trace_Suite SHALL enforce access level restrictions (tuning, regression, holdout)

### Requirement 9: Controller Profile

**User Story:** As a conversion lab operator, I want to define canonical controller profiles with all controls, ranges, units, and coordinate frames, so that traces are unambiguous.

#### Acceptance Criteria

1. WHEN defining a controller profile, THE Controller_Profile SHALL declare all buttons with ID, name, and type
2. WHEN defining a controller profile, THE Controller_Profile SHALL declare all axes with ID, name, type, neutral value, range, and unit
3. WHEN defining a controller profile, THE Controller_Profile SHALL declare all triggers with ID, name, type, neutral value, range, and unit
4. WHEN defining a controller profile with gyro, THE Controller_Profile SHALL declare axes (pitch, yaw, roll), unit, range, sample rate, and coordinate frame
5. WHEN defining a controller profile with accel, THE Controller_Profile SHALL declare axes, unit, range, sample rate, and coordinate frame
6. WHEN defining canonical profile v1, THE Controller_Profile SHALL be based on extended gyro gamepad (8BitDo Ultimate 2 Wireless)
7. WHEN defining canonical profile v1, THE Controller_Profile SHALL exclude touchpad position, touchpad surface, adaptive triggers, and microphone button

### Requirement 10: Trace Determinism

**User Story:** As a conversion lab operator, I want trace execution to be deterministic, so that repeated runs produce consistent results.

#### Acceptance Criteria

1. WHEN executing the same trace against the same config multiple times, THE system SHALL produce identical event sequences within timing tolerance
2. WHEN comparing repeated runs, THE system SHALL verify that all event sequences match within the configured timing tolerance
3. WHEN using headless JSM, THE system SHALL use deterministic trace-time instead of real-time to eliminate timing variance

### Requirement 11: Platform Parity

**User Story:** As a conversion lab operator, I want to validate that Linux lab results transfer to Windows, so that I can develop on Linux and deploy on Windows.

#### Acceptance Criteria

1. WHEN running the same trace on Linux and Windows, THE system SHALL produce equivalent results within platform-specific delta tolerances
2. WHEN platform differences are detected, THE system SHALL record them in the Platform_Delta_Catalog
3. WHEN platform differences are detected, THE system SHALL distinguish them from conversion failures to avoid false negatives
4. WHEN validating platform parity, THE system SHALL execute key traces on both platforms before expensive infrastructure work

### Requirement 12: Headless JSM Parity

**User Story:** As a conversion lab operator, I want to accelerate iteration with headless JSM after proving parity with real JSM, so that I can run more experiments faster.

#### Acceptance Criteria

1. WHEN certifying headless JSM for a feature class, THE system SHALL execute the same traces through real JSM and headless JSM
2. WHEN certifying headless JSM for a feature class, THE system SHALL verify that event streams match within feature-class tolerances
3. WHEN certifying headless JSM on Windows, THE system SHALL repeat parity tests for each feature class
4. WHEN using headless JSM, THE system SHALL use deterministic trace-time to eliminate timing variance

### Requirement 13: Non-Regression Acceptance

**User Story:** As a conversion lab operator, I want to prevent quality degradation, so that converter iterations only improve or maintain conversion quality.

#### Acceptance Criteria

1. WHEN accepting a conversion change, THE system SHALL verify that no feature regresses without explicit justification
2. WHEN a feature regresses, THE system SHALL require justification naming affected feature, user-visible loss, unavoidability reason, and follow-up task
3. WHEN a feature improves in error metric, THE system SHALL ensure classification does not worsen
4. WHEN a regression is detected, THE system SHALL halt acceptance until justification is provided or change is reverted

### Requirement 14: Adversarial Trace Generation

**User Story:** As a conversion lab operator, I want to automatically generate traces that expose behavioral differences, so that I can comprehensively test conversion quality.

#### Acceptance Criteria

1. WHEN generating adversarial traces, THE Adversarial_Trace_Generator SHALL create traces targeting specific features, boundaries, compositions, mutations, regressions, and holdouts
2. WHEN generating feature-directed traces, THE Adversarial_Trace_Generator SHALL target specific features (activators, layers, chords, gyro, sticks, triggers)
3. WHEN generating boundary traces, THE Adversarial_Trace_Generator SHALL target timing windows, deadzones, thresholds, and release order
4. WHEN generating composition traces, THE Adversarial_Trace_Generator SHALL combine mode shifts, chords, gyro enable states, and analog movement
5. WHEN generating mutation traces, THE Adversarial_Trace_Generator SHALL apply small perturbations to timing and axis values
6. WHEN generating regression traces, THE Adversarial_Trace_Generator SHALL create traces for previously discovered deltas
7. WHEN generating holdout traces, THE Adversarial_Trace_Generator SHALL withhold trace contents from converter agents
8. WHEN generating any trace, THE Adversarial_Trace_Generator SHALL include an intent field explaining what behavioral difference the trace exposes

### Requirement 15: Agent Task Isolation

**User Story:** As a conversion lab operator, I want agents to execute bounded tasks with clear inputs, outputs, and acceptance criteria, so that I can reason about agent behavior.

#### Acceptance Criteria

1. WHEN defining an agent task, THE Task_Brief SHALL specify owner role, input files, output files, commands, environment, acceptance criteria, and stop criteria
2. WHEN a Validator_Agent executes, THE Task_Brief SHALL limit inputs to trace suite and configs, and outputs to run artifacts
3. WHEN a Converter_Agent executes, THE Task_Brief SHALL limit inputs to loss reports and knowledge base, and outputs to candidate configs
4. WHEN an Adversarial_Trace_Generator executes, THE Task_Brief SHALL limit inputs to cycle history and deltas, and outputs to new traces

### Requirement 16: JSM Build and Runtime

**User Story:** As a conversion lab operator, I want to build and run JSM on Linux with minimal semantic changes, so that I can develop the lab on Linux.

#### Acceptance Criteria

1. WHEN building JSM on Linux, THE system SHALL configure CMake for Linux with SDL3 backend
2. WHEN building JSM on Linux, THE system SHALL produce a JoyShockMapper executable
3. WHEN running JSM on Linux, THE system SHALL capture keyboard, mouse, and virtual gamepad output
4. WHEN using headless JSM, THE system SHALL inject synthetic input through a synthetic JslWrapper without semantic changes to JSM runtime
5. WHEN building JSM on Linux, THE system SHALL limit changes to build files, dependency detection, and platform glue (non-semantic changes only)

### Requirement 17: Cycle History Tracking

**User Story:** As a conversion lab operator, I want to track error metrics, trends, and classifications across converter cycles, so that I can measure progress and detect stop conditions.

#### Acceptance Criteria

1. WHEN recording a cycle, THE Cycle_History SHALL include cycle number, timestamp, current error, previous error, best error, trend, classification, confidence, and stop reason
2. WHEN computing trend, THE Cycle_History SHALL compare current error to previous error and classify as new, improved, regressed, unchanged, or incomparable
3. WHEN computing best error, THE Cycle_History SHALL track the minimum error across all cycles
4. WHEN recording metrics, THE Cycle_History SHALL include metric name, unit, comparison rule (minimize, maximize, target), and target value
5. WHEN recording confidence, THE Cycle_History SHALL use a value in range [0.0, 1.0]
6. WHEN tracking per feature, THE Cycle_History SHALL maintain separate cycle records for each feature and trace combination
7. WHEN a stop condition is met, THE Cycle_History SHALL record the stop reason (exact, under_tolerance, plateaued, oscillating, unsupported, max_cycles, blocked_by_mapper_capability, blocked_by_regression_risk)

### Requirement 18: Artifact Schemas

**User Story:** As a conversion lab operator, I want all artifacts to validate against stable JSON schemas, so that agents can reliably parse and generate artifacts.

#### Acceptance Criteria

1. THE system SHALL define a JSON Schema for trace format with Trace, Frame, ButtonState, AxisState, GyroState, AccelState, TraceMetadata
2. THE system SHALL define a JSON Schema for normalized events with NormalizedEvent, NormalizedEvents, NormalizationMetadata
3. THE system SHALL define a JSON Schema for delta format with Delta, ExactMatch, TolerantMatch, MissingEvent, ExtraEvent, TimingDelta, ValueDelta, SequenceDelta
4. THE system SHALL define a JSON Schema for loss report format with LossReport, FeatureLoss, LossSummary, Classification, StopReason
5. THE system SHALL define a JSON Schema for cycle history format with CycleHistory, CycleRecord, Metric
6. THE system SHALL define a JSON Schema for run manifest format with RunManifest, Environment, MapperVersions, MapperVersion, ArtifactPaths
7. THE system SHALL define a JSON Schema for knowledge base entries with ControlSemantics, FunctionSemantics, EquivalenceRule, Provenance, EvidenceLink

### Requirement 19: Error Handling

**User Story:** As a conversion lab operator, I want the system to handle errors gracefully and provide clear diagnostics, so that I can debug failures.

#### Acceptance Criteria

1. WHEN trace execution fails, THE system SHALL abort the run, write error to run manifest, preserve partial artifacts with error marker, and not emit delta or loss reports
2. WHEN output capture times out, THE system SHALL mark capture as incomplete, record timeout in metadata, emit partial events with timeout marker, and continue to comparison with incomplete flag
3. WHEN event normalization fails, THE system SHALL log unrecognized events, emit normalized events for recognized subset, mark normalization as partial, and continue with warning
4. WHEN comparison rules conflict, THE system SHALL use the most conservative (strictest) rule, log conflict, mark delta with conflict warning, and continue comparison
5. WHEN converter oscillation is detected, THE system SHALL set stop reason to 'oscillating', emit loss report with oscillation details, and halt iteration for that feature
6. WHEN knowledge base conflict is detected, THE system SHALL append observation to lab notes with conflict marker, not overwrite canonical entry, escalate to knowledge curator, and continue using existing canonical entry

### Requirement 20: Phase Gate Criteria

**User Story:** As a conversion lab operator, I want explicit gate criteria between implementation phases, so that I validate foundational work before expensive downstream tasks.

#### Acceptance Criteria

1. WHEN completing Phase 1, THE system SHALL verify Linux build succeeds, smoke test passes or block reason documented, Windows smoke test matches Linux results, and decision documented in linux-lab-decision.md
2. WHEN completing Phase 2, THE system SHALL verify one trace drives both mappers, both outputs captured as typed events, delta computed and written, and Windows validation completed or explicitly blocked
3. WHEN completing Phase 3, THE system SHALL verify all schemas have JSON Schema definitions, validating examples exist for each schema, and schema versioning strategy documented
4. WHEN completing Phase 4, THE system SHALL verify one orchestration run produces all artifacts, artifacts validate against schemas, and run is repeatable with same results
5. WHEN completing Phase 5, THE system SHALL verify each feature class has parity certification, headless JSM matches real JSM within tolerances, and parity tests run on Windows
6. WHEN completing Phase 6, THE system SHALL verify adversarial trace generator writes versioned suites, trace manifests include intent and targeted features, and tuning/regression/holdout access rules enforced
7. WHEN completing Phase 7, THE system SHALL verify canonical entries require real-runtime evidence, promotion rules enforced, and conflict handling documented
8. WHEN completing Phase 8, THE system SHALL verify converter produces candidate config and loss report, cycle history tracks improvement/regression/plateau, no unaccepted regressions, and Windows regression suite passes

