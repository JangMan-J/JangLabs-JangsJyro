# Design Document: Gamepad Mapper Conversion Lab

## Overview

The Gamepad Mapper Conversion Lab is an agent-first behavioral testing system for converting gamepad mapper configurations between Steam Input and JoyShockMapper (JSM). Unlike syntax-only converters, this lab measures actual runtime behavior by comparing real Steam Input output against real JSM output given identical controller input traces. The system supports bidirectional conversion architecture (Steam Input ↔ JSM), though initial implementation focuses on Steam Input → JSM.

The lab enables isolated agent workflows through structured artifacts, adversarial trace generation, and a reference knowledge base. Validation is conservative and per-feature, with early Windows parity gates ensuring Linux automation results transfer to production environments. The system tracks exact matches, bounded approximations, degraded approximations, unsupported features, and user-choice-required scenarios independently, with cycle history tracking improvement trends and stop reasons.

## Architecture

### System Overview

```mermaid
graph TB
    subgraph Input
        TraceRunner[Trace Runner]
        TraceFiles[Trace Files]
    end
    
    subgraph Reference Lane
        SteamInput[Steam Input Runtime]
        RefObserver[Reference Output Observer]
    end
    
    subgraph Candidate Lane
        JSMRuntime[JSM Runtime]
        CandObserver[Candidate Output Observer]
    end
    
    subgraph Analysis
        Normalizer[Event Normalizer]
        Comparator[Behavior Comparator]
        Converter[Config Converter]
    end
    
    subgraph Knowledge
        KnowledgeBase[(Knowledge Base)]
        LabNotes[(Lab Notes)]
    end
    
    subgraph Agents
        ValidatorAgent[Validator Agent]
        ConverterAgent[Converter Agent]
        AdversarialAgent[Adversarial Trace Generator]
        CuratorAgent[Knowledge Curator]
    end
    
    TraceFiles --> TraceRunner
    TraceRunner --> SteamInput
    TraceRunner --> JSMRuntime
    
    SteamInput --> RefObserver
    JSMRuntime --> CandObserver
    
    RefObserver --> Normalizer
    CandObserver --> Normalizer
    
    Normalizer --> Comparator
    Comparator --> Converter
    
    Converter --> KnowledgeBase
    Comparator --> LabNotes
    
    KnowledgeBase --> ConverterAgent
    LabNotes --> CuratorAgent
    
    AdversarialAgent --> TraceFiles
    ValidatorAgent --> Comparator
    ConverterAgent --> Converter
    CuratorAgent --> KnowledgeBase
