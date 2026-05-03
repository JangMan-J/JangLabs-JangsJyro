# Implementation Plan: JyroPort

## Overview

JyroPort is an agent-first behavioral conversion lab for gamepad mapper configurations. The implementation follows an 8-phase approach with strict gate criteria between phases. Each phase builds foundational capabilities before expensive downstream work begins. The system compares real Steam Input versus real JSM runtime behavior to measure conversion quality, tracking improvement/regression/plateau across converter cycles.

This implementation plan breaks down each phase into discrete coding tasks. Tasks reference specific requirements from the requirements document and build incrementally toward a complete conversion lab with adversarial trace generation, evidence-backed knowledge base, and iterative converter agents.

## Tasks

### Phase 1: Feasibility Gates

- [-] 1. Set up Linux build infrastructure for JSM
  - [ ] 1.1 Configure CMake for Linux build with SDL3 backend
    - Modify `CMakeLists.txt` and `cmake/LinuxConfig.cmake` for Linux compatibility
    - Ensure non-semantic changes only (build files, dependency detection, platform glue)
    - _Requirements: 16.1, 16.5_
  
  - [ ] 1.2 Build JSM on Linux and verify executable
    - Run CMake configuration and build
    - Verify `JoyShockMapper` executable is created
    - _Requirements: 20.1_
  
  - [ ] 1.3 Create minimal smoke test config (S = SPACE, ZR = LMOUSE)
    - Write minimal JSM config file with two button mappings
    - Place in `dist/smoke-test.txt`
    - _Requirements: 20.1_

- [ ] 2. Run Linux smoke test and capture results
  - [ ] 2.1 Execute JSM with smoke test config on Linux
    - Run JSM with smoke test config
    - Manually verify button mappings work or document block reason
    - _Requirements: 20.1_
  
  - [ ] 2.2 Document Linux smoke test results
    - Record success or failure with detailed error messages
    - Document any platform-specific issues
    - _Requirements: 11.3, 20.1_

- [ ] 3. Run Windows smoke test and validate parity
  - [ ] 3.1 Execute JSM with smoke test config on Windows
    - Run same smoke test config on Windows
    - Verify button mappings work
    - _Requirements: 11.1, 20.1_
  
  - [ ] 3.2 Compare Linux and Windows smoke test results
    - Document any behavioral differences
    - Record platform deltas in platform delta catalog
    - _Requirements: 11.3, 11.4_
  
  - [ ] 3.3 Write linux-lab-decision.md
    - Document decision: linux-main, linux-build-only, or linux-rejected
    - Justify decision based on smoke test results
    - _Requirements: 20.1_

- [ ] 4. Checkpoint - Phase 1 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 2: Steam/JSM A-B Proof

- [ ] 5. Set up virtual controller input infrastructure
  - [ ] 5.1 Implement virtual controller driver integration for Linux
    - Integrate with uinput for virtual gamepad creation
    - Support button and axis state injection
    - _Requirements: 1.2, 1.3_
  
  - [ ] 5.2 Implement virtual controller driver integration for Windows
    - Integrate with ViGEm for virtual gamepad creation
    - Support button and axis state injection
    - _Requirements: 1.2, 1.3_
  
  - [ ] 5.3 Create TraceRunner component with frame emission
    - Implement `TraceRunner` interface from design
    - Support loading trace files and emitting frames with microsecond timestamps
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 6. Implement output capture for Steam Input
  - [ ] 6.1 Create OutputObserver component for keyboard events
    - Capture keyboard scancodes and key events with timestamps
    - Use evdev on Linux, raw input on Windows
    - _Requirements: 2.1, 2.2_
  
  - [ ] 6.2 Extend OutputObserver for mouse events
    - Capture mouse button, movement, and wheel events with timestamps
    - _Requirements: 2.3_
  
  - [ ] 6.3 Extend OutputObserver for virtual gamepad events
    - Capture virtual gamepad button and axis state with timestamps
    - _Requirements: 2.4_
  
  - [ ] 6.4 Add motion output capture (when observable)
    - Record motion events if available
    - _Requirements: 2.5_

- [ ] 7. Implement output capture for JSM
  - [ ] 7.1 Integrate OutputObserver with JSM runtime
    - Capture JSM keyboard, mouse, and gamepad output
    - Ensure isolation from Steam Input capture
    - _Requirements: 2.1, 2.6_

- [ ] 8. Create controlled trace and hand-authored JSM config
  - [ ] 8.1 Create minimal controlled trace file
    - Define trace format with version, profile, frames, metadata
    - Create trace with simple button presses (e.g., S button, ZR trigger)
    - _Requirements: 1.1, 9.1, 9.2, 9.3_
  
  - [ ] 8.2 Write hand-authored equivalent JSM config
    - Create JSM config that should produce same output as Steam Input
    - Document expected equivalence
    - _Requirements: 5.1_

- [ ] 9. Execute A-B comparison
  - [ ] 9.1 Drive Steam Input with controlled trace
    - Execute trace against Steam Input
    - Capture output events
    - _Requirements: 1.2, 2.6_
  
  - [ ] 9.2 Drive JSM with controlled trace
    - Execute same trace against JSM with hand-authored config
    - Capture output events
    - _Requirements: 1.2, 2.6_
  
  - [ ] 9.3 Implement EventNormalizer component
    - Normalize keyboard, mouse, and gamepad events to canonical format
    - Map platform-specific scancodes to canonical key names
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ] 9.4 Implement Comparator component
    - Compare reference and candidate event streams
    - Compute exact matches, tolerant matches, missing/extra events
    - Compute timing and value deltas
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_
  
  - [ ] 9.5 Write delta to structured JSON file
    - Output delta with exact, tolerant, missing, extra, timing, value, sequence fields
    - _Requirements: 7.7_

- [ ] 10. Validate Windows parity for Phase 2
  - [ ] 10.1 Repeat A-B comparison on Windows
    - Execute same trace against both mappers on Windows
    - Capture and compare outputs
    - _Requirements: 11.1, 11.2, 20.2_
  
  - [ ] 10.2 Document Windows parity results
    - Record any platform-specific differences
    - Update platform delta catalog
    - _Requirements: 11.3, 11.4_

- [ ] 11. Checkpoint - Phase 2 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 3: Artifact Contracts

- [ ] 12. Define trace format schema
  - [ ] 12.1 Create JSON Schema for trace format
    - Define Trace, Frame, ButtonState, AxisState, GyroState, AccelState, TraceMetadata
    - Include version, profile, frames, metadata fields
    - _Requirements: 18.1, 20.3_
  
  - [ ] 12.2 Create validating examples for trace format
    - Write example trace files that validate against schema
    - Include edge cases (empty trace, single frame, long trace)
    - _Requirements: 20.3_

- [ ] 13. Define normalized event format schema
  - [ ] 13.1 Create JSON Schema for normalized events
    - Define NormalizedEvent, NormalizedEvents, NormalizationMetadata
    - Include timestamp, type, action, target, value, metadata fields
    - _Requirements: 18.2, 20.3_
  
  - [ ] 13.2 Create validating examples for normalized events
    - Write example event files for each event type
    - _Requirements: 20.3_

- [ ] 14. Define delta, loss, and cycle-history schemas
  - [ ] 14.1 Create JSON Schema for delta format
    - Define Delta, ExactMatch, TolerantMatch, MissingEvent, ExtraEvent, TimingDelta, ValueDelta, SequenceDelta
    - _Requirements: 18.3, 20.3_
  
  - [ ] 14.2 Create JSON Schema for loss report format
    - Define LossReport, FeatureLoss, LossSummary, Classification, StopReason
    - _Requirements: 18.4, 20.3_
  
  - [ ] 14.3 Create JSON Schema for cycle history format
    - Define CycleHistory, CycleRecord, Metric
    - Include validation rules for sequential cycle numbers, non-negative errors
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 18.5, 20.3_
  
  - [ ] 14.4 Create validating examples for delta, loss, and cycle-history
    - Write example files for each schema
    - _Requirements: 20.3_

- [ ] 15. Define run manifest and environment schema
  - [ ] 15.1 Create JSON Schema for run manifest
    - Define RunManifest, Environment, MapperVersions, MapperVersion, ArtifactPaths
    - Include validation rules for unique UUID, ISO 8601 timestamps, SHA-256 hashes
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 18.6, 20.3_
  
  - [ ] 15.2 Create validating examples for run manifest
    - Write example manifest files
    - _Requirements: 20.3_

- [ ] 16. Define knowledge base schemas
  - [ ] 16.1 Create JSON Schema for knowledge base entries
    - Define ControlSemantics, FunctionSemantics, EquivalenceRule, Provenance, EvidenceLink
    - Include validation rules for real-runtime evidence requirement
    - _Requirements: 6.5, 6.6, 18.7, 20.3_
  
  - [ ] 16.2 Create validating examples for knowledge base entries
    - Write example canonical entries with provenance
    - Write example lab notes
    - _Requirements: 20.3_
  
  - [ ] 16.3 Document schema versioning strategy
    - Define how schemas evolve over time
    - Document backward compatibility rules
    - _Requirements: 20.3_

- [ ] 17. Checkpoint - Phase 3 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 4: Real Runtime Harness

- [ ] 18. Generalize Steam Input lane
  - [ ] 18.1 Create MapperTarget abstraction
    - Define interface for mapper targets (Steam Input, JSM)
    - Support configuration loading and runtime execution
    - _Requirements: 1.2, 1.3_
  
  - [ ] 18.2 Implement Steam Input MapperTarget
    - Integrate with Steam Input runtime
    - Support layout loading and virtual input
    - _Requirements: 1.2_

- [ ] 19. Generalize JSM lane
  - [ ] 19.1 Implement JSM MapperTarget
    - Integrate with JSM runtime
    - Support config loading and virtual input
    - _Requirements: 1.2_

- [ ] 20. Add comprehensive output observers
  - [ ] 20.1 Extend OutputObserver for all event types
    - Ensure keyboard, mouse, virtual gamepad, motion capture is complete
    - Add haptics capture (future placeholder)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 20.2 Add capture status and error handling
    - Implement getCaptureStatus method
    - Handle capture timeouts and incomplete captures
    - _Requirements: 19.2_

- [ ] 21. Implement configurable comparison rules
  - [ ] 21.1 Create ComparisonRules configuration
    - Define exact match types, timing tolerance, value tolerance, sequence rules
    - Support loading rules from configuration files
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 21.2 Extend Comparator with configurable rules
    - Apply comparison rules during event matching
    - Handle rule conflicts with conservative fallback
    - _Requirements: 4.1, 19.4_

- [ ] 22. Build run orchestration
  - [ ] 22.1 Create RunOrchestrator component
    - Coordinate trace execution, output capture, normalization, comparison
    - Generate run ID and capture environment metadata
    - _Requirements: 7.1, 7.2, 7.5_
  
  - [ ] 22.2 Implement artifact generation
    - Write run manifest, reference events, candidate events, delta, loss report
    - Validate all artifacts against schemas
    - _Requirements: 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6_
  
  - [ ] 22.3 Add human-readable report generation
    - Generate summary report from structured artifacts
    - _Requirements: 7.10_

- [ ] 23. Verify run repeatability
  - [ ] 23.1 Execute same run multiple times
    - Run same trace against same config 10 times
    - Verify event sequences match within timing tolerance
    - _Requirements: 10.1, 10.2_
  
  - [ ] 23.2 Validate artifact consistency
    - Verify all artifacts are generated correctly
    - Validate against schemas
    - _Requirements: 20.4_

- [ ] 24. Checkpoint - Phase 4 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 5: Headless Acceleration

- [ ] 25. Implement synthetic input for JSM
  - [ ] 25.1 Create synthetic JslWrapper for input injection
    - Replace device discovery with synthetic input provider
    - Feed existing JSM runtime path without semantic changes
    - _Requirements: 16.4_
  
  - [ ] 25.2 Add deterministic trace-time control
    - Replace real-time with deterministic time from trace
    - Eliminate timing variance
    - _Requirements: 10.3, 12.4_

- [ ] 26. Implement output recording for headless JSM
  - [ ] 26.1 Add keyboard/mouse output recording
    - Record keyboard and mouse events from headless JSM
    - _Requirements: 16.3_
  
  - [ ] 26.2 Add virtual gamepad output recording
    - Record virtual gamepad button and axis state from headless JSM
    - _Requirements: 16.3_

- [ ] 27. Certify headless JSM parity per feature class
  - [ ] 27.1 Define feature classes for parity certification
    - Identify feature classes: basic buttons, analog sticks, triggers, gyro, layers, chords, activators
    - _Requirements: 12.1, 12.2_
  
  - [ ] 27.2 Run parity tests for each feature class
    - Execute same traces through real JSM and headless JSM
    - Compare event streams within feature-class tolerances
    - _Requirements: 12.1, 12.2, 12.4_
  
  - [ ] 27.3 Validate parity on Windows
    - Repeat parity tests on Windows for each feature class
    - _Requirements: 12.3, 20.5_
  
  - [ ] 27.4 Document parity certification results
    - Record which feature classes are certified for headless acceleration
    - Document any feature classes that fail parity
    - _Requirements: 12.1, 12.2_

- [ ] 28. Checkpoint - Phase 5 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 6: Trace Intelligence

- [ ] 29. Create baseline trace suite
  - [ ] 29.1 Define canonical controller profile v1
    - Define extended gyro gamepad profile (8BitDo Ultimate 2 Wireless)
    - Declare all buttons, axes, triggers, gyro, accel with ranges, units, coordinate frames
    - Exclude touchpad position, touchpad surface, adaptive triggers, microphone button
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  
  - [ ] 29.2 Create baseline traces for common scenarios
    - Create traces for: single button press, button hold, button release, stick movement, trigger pull, gyro rotation
    - Include intent field explaining what each trace tests
    - _Requirements: 8.2, 8.6, 14.1_
  
  - [ ] 29.3 Create TraceSuite management component
    - Implement TraceSuite, TraceRef, TraceMetadata interfaces
    - Support versioned suites with immutable traces
    - _Requirements: 8.1, 8.2, 8.3, 8.5_

- [ ] 30. Implement adversarial trace generator agent
  - [ ] 30.1 Create AdversarialTraceGenerator component
    - Implement agent interface for trace generation
    - Support feature-directed, boundary, composition, mutation, regression, holdout traces
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8_
  
  - [ ] 30.2 Implement feature-directed trace generation
    - Generate traces targeting specific features: activators, layers, chords, gyro, sticks, triggers
    - _Requirements: 14.2_
  
  - [ ] 30.3 Implement boundary trace generation
    - Generate traces around timing windows, deadzones, thresholds, release order
    - _Requirements: 14.3_
  
  - [ ] 30.4 Implement composition trace generation
    - Generate traces combining mode shifts, chords, gyro enable states, analog movement
    - _Requirements: 14.4_
  
  - [ ] 30.5 Implement mutation trace generation
    - Generate traces with small perturbations of timing and axis values
    - _Requirements: 14.5_
  
  - [ ] 30.6 Implement regression trace generation
    - Generate traces for previously discovered deltas
    - _Requirements: 14.6_
  
  - [ ] 30.7 Implement holdout trace generation
    - Generate traces withheld from converter tuning
    - _Requirements: 14.7_

- [ ] 31. Enforce trace suite access rules
  - [ ] 31.1 Implement access level enforcement
    - Support tuning, regression, holdout access levels
    - Prevent converter agents from accessing holdout trace contents
    - _Requirements: 8.4, 8.7_
  
  - [ ] 31.2 Create trace suite manifest with intent
    - Include trace ID, path, hash, targeted features, intent for each trace
    - _Requirements: 8.2, 8.6, 20.6_

- [ ] 32. Checkpoint - Phase 6 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 7: Knowledge Base

- [ ] 33. Implement knowledge base storage
  - [ ] 33.1 Create KnowledgeBase component
    - Implement queryControl, queryMapperFunction, queryEquivalence, getCapabilityMatrix methods
    - Support JSON file storage for canonical entries and lab notes
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ] 33.2 Define provenance tracking structure
    - Record run ID, trace ID, mapper version, platform, device profile, confidence, validation date
    - _Requirements: 6.5_

- [ ] 34. Implement lab notes recording
  - [ ] 34.1 Create LabNotes component
    - Record agent observations from runs
    - Link observations to evidence (run ID, trace ID, delta, loss report)
    - _Requirements: 6.5_
  
  - [ ] 34.2 Add conflict detection for lab notes
    - Detect when new observation contradicts existing canonical entry
    - Append to lab notes with conflict marker
    - _Requirements: 6.7, 19.6_

- [ ] 35. Implement knowledge promotion rules
  - [ ] 35.1 Create KnowledgeCurator agent component
    - Review lab notes for promotion to canonical knowledge
    - Enforce real-runtime evidence requirement
    - _Requirements: 6.6, 20.7_
  
  - [ ] 35.2 Implement promotion validation
    - Validate that canonical entries have at least one real-runtime evidence link
    - Reject entries without provenance
    - _Requirements: 6.6_
  
  - [ ] 35.3 Document conflict resolution process
    - Define how curator resolves conflicts between observations
    - Support conditional rules and scope splitting
    - _Requirements: 19.6, 20.7_

- [ ] 36. Build capability matrix
  - [ ] 36.1 Create CapabilityMatrix component
    - Catalog mapper capabilities (Steam Input vs JSM)
    - Track which features are supported, approximated, or unsupported
    - _Requirements: 6.4_
  
  - [ ] 36.2 Populate initial capability matrix
    - Document known Steam Input and JSM capabilities
    - Mark areas requiring investigation
    - _Requirements: 6.4_

- [ ] 37. Checkpoint - Phase 7 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Phase 8: Converter Work

- [ ] 38. Implement Steam Input layout parser
  - [ ] 38.1 Create SteamInputParser component
    - Parse Steam Input layout files (VDF format)
    - Extract button mappings, activators, layers, gyro settings
    - _Requirements: 5.1_
  
  - [ ] 38.2 Handle Steam Input layout variations
    - Support different layout versions and formats
    - Handle missing or optional fields gracefully
    - _Requirements: 5.1_

- [ ] 39. Implement JSM config emitter
  - [ ] 39.1 Create JSMEmitter component
    - Generate syntactically valid JSM config files
    - Emit clean runnable configs without explanatory comments
    - _Requirements: 5.3, 7.11_
  
  - [ ] 39.2 Implement JSM syntax validation
    - Validate generated configs against JSM syntax rules
    - Catch syntax errors before runtime testing
    - _Requirements: 5.3_

- [ ] 40. Implement loss classifier
  - [ ] 40.1 Create LossClassifier component
    - Classify each feature as exact, bounded approximation, degraded approximation, unsupported, or requires user choice
    - Provide explanations with evidence links
    - _Requirements: 5.4, 5.5_
  
  - [ ] 40.2 Implement confidence scoring
    - Compute confidence scores for classifications
    - Track confidence across converter cycles
    - _Requirements: 5.5, 17.6_

- [ ] 41. Implement Converter component
  - [ ] 41.1 Create Converter with convert and repair methods
    - Implement convert method for initial conversion
    - Implement repair method for iterative improvement
    - _Requirements: 5.1, 5.2, 5.6_
  
  - [ ] 41.2 Integrate knowledge base queries
    - Query control semantics, mapper function semantics, equivalence rules
    - Use knowledge base to inform conversion decisions
    - _Requirements: 5.2_
  
  - [ ] 41.3 Implement cycle history tracking
    - Track error metrics, trends, confidence per feature across cycles
    - Compute trend (new, improved, regressed, unchanged, incomparable)
    - _Requirements: 5.7, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_
  
  - [ ] 41.4 Implement stop condition detection
    - Detect exact, under tolerance, plateaued, oscillating, unsupported, max cycles, blocked by mapper capability, blocked by regression risk
    - Set stop reason when condition is met
    - _Requirements: 5.8, 17.7, 19.5_

- [ ] 42. Implement iterative repair loop
  - [ ] 42.1 Create ConverterAgent component
    - Orchestrate converter cycles
    - Update conversion rules based on loss reports
    - _Requirements: 5.6, 5.7_
  
  - [ ] 42.2 Implement non-regression acceptance policy
    - Check all features for regressions before accepting changes
    - Require justification for any regressions
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 20.8_
  
  - [ ] 42.3 Add regression justification documentation
    - Require naming affected feature, user-visible loss, unavoidability reason, follow-up task
    - _Requirements: 13.2_

- [ ] 43. Build Windows regression suite
  - [ ] 43.1 Create Windows-specific regression traces
    - Identify Windows-specific behaviors and edge cases
    - Create traces targeting Windows platform deltas
    - _Requirements: 11.1, 11.2, 20.8_
  
  - [ ] 43.2 Run Windows regression suite
    - Execute regression suite on Windows
    - Verify no regressions in Windows-specific behaviors
    - _Requirements: 20.8_

- [ ] 44. Implement agent task isolation
  - [ ] 44.1 Create TaskBrief component
    - Define task briefs with owner role, input files, output files, commands, environment, acceptance criteria, stop criteria
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [ ] 44.2 Implement ValidatorAgent interface
    - Define agent interface for running trace suites and comparing event streams
    - _Requirements: 15.1_
  
  - [ ] 44.3 Implement ConverterAgent interface
    - Define agent interface for updating conversion rules and generating candidate configs
    - _Requirements: 15.1_
  
  - [ ] 44.4 Implement AdversarialTraceGenerator interface
    - Define agent interface for creating traces that expose behavioral differences
    - _Requirements: 15.1_
  
  - [ ] 44.5 Implement KnowledgeCurator interface
    - Define agent interface for promoting evidence-backed observations to canonical knowledge
    - _Requirements: 15.1_

- [ ] 45. Final checkpoint - Phase 8 gate evaluation
  - Ensure all tests pass, ask the user if questions arise.

### Future Work (Not in Current Scope)

- [ ] 46. Add JSM-to-Steam conversion path
  - Implement JSM config parser
  - Implement Steam Input layout emitter
  - Adapt converter for reverse direction
  - _Note: Architectural support exists, but implementation deferred_

## Notes

- All tasks reference specific requirements for traceability
- Checkpoints ensure incremental validation at phase boundaries
- Phase gates enforce foundational work before expensive downstream tasks
- Windows parity validation occurs early (Phase 1, Phase 2) and throughout
- Headless JSM acceleration requires parity certification per feature class
- Knowledge base promotion requires real-runtime evidence
- Non-regression acceptance policy prevents quality degradation
- Agent task isolation enables independent execution with bounded inputs/outputs
- TypeScript interfaces from design document guide implementation structure
