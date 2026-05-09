# ACP Orchestration - Quick Start

## What You Now Have

I've built a complete system that lets me (Kiro/Claude) orchestrate multiple Codex agents via the Agent Client Protocol. This gives you **real-time visibility** into AI agent sessions while they work on your JSM codebase.

## 🎯 Key Capabilities

1. **Spawn Codex Agents** - I can launch any Codex model (gpt-5.5, gpt-5.4, gpt-5.3-codex, etc.)
2. **Parallel Coordination** - Multiple agents can work simultaneously on different aspects
3. **Real-Time Visibility** - You can watch sessions live as they execute
4. **Result Synthesis** - I compare and combine findings from multiple agents
5. **Full Transparency** - Every message is logged for review

## 🚀 Quick Examples

### Example 1: Single Agent Task
```bash
python3 .acp-sessions/acp-bridge.py "$(pwd)" \
  "Explain the SDL3 wrapper architecture" \
  "gpt-5.4"
```

**Watch it live:**
```bash
tail -f .acp-sessions/session_*.log
```

**View results:**
```bash
python3 .acp-sessions/view-session.py
```

### Example 2: Multi-Agent Analysis
```bash
python3 .acp-sessions/acp-orchestrator.py \
  "Identify the best approach for migrating input handling to SDL3"
```

This spawns 3 agents in parallel:
- **fast-scout** (gpt-5.3-codex-spark) - Quick initial scan
- **deep-analyzer** (gpt-5.4) - Detailed analysis
- **specialist** (gpt-5.3-codex) - Implementation-focused review

**Results in:** `.acp-sessions/run_TIMESTAMP/report.md`

## 📊 Real-Time Visibility

### Option 1: Watch Log Files
```bash
# Watch orchestrator
tail -f .acp-sessions/run_*/orchestrator.log

# Watch specific agent
tail -f .acp-sessions/session_fast-scout_*.log
```

### Option 2: Open in Editor
The log files update in real-time. Open them in your editor and watch them stream.

### Option 3: Review After Completion
```bash
python3 .acp-sessions/view-session.py
```

Shows formatted output:
```
👤 USER: <your prompt>
🤖 AGENT: <agent's response>
🔧 TOOL CALLS: <what tools the agent used>
```

## 🎨 Orchestration Patterns

### Pattern: Parallel Diagnosis
**Use Case:** Complex architectural decisions

```
Me (Kiro): "Should we migrate to SDL3?"
  ├─ Agent 1 (gpt-5.5): Research SDL3 capabilities
  ├─ Agent 2 (gpt-5.4): Analyze current JSL usage
  └─ Agent 3 (gpt-5.3-codex): Estimate migration effort
  
Me: Compare results → Synthesize recommendation → Present to you
```

### Pattern: Implement + Review
**Use Case:** High-quality feature implementation

```
Me (Kiro): "Implement gyro calibration"
  ├─ Agent 1 (gpt-5.3-codex): Write implementation
  └─ Agent 2 (gpt-5.4): Review for bugs/edge cases
  
Me: Incorporate feedback → Present final code
```

### Pattern: Divide and Conquer
**Use Case:** Large refactoring

```
Me (Kiro): "Refactor input handling"
  ├─ Agent 1: Refactor Windows code
  ├─ Agent 2: Refactor Linux code
  └─ Agent 3: Update shared interfaces
  
Me: Ensure consistency → Merge changes
```

## 🔧 Available Models

| Model | Speed | Best For |
|-------|-------|----------|
| gpt-5.5 | ⭐ | Complex architecture, research |
| gpt-5.4 | ⭐⭐⭐ | Everyday coding |
| gpt-5.4-mini | ⭐⭐⭐⭐⭐ | Quick tasks |
| gpt-5.3-codex | ⭐⭐⭐ | Code implementation |
| gpt-5.3-codex-spark | ⭐⭐⭐⭐⭐ | Ultra-fast scanning |
| gpt-5.2 | ⭐ | Long-running agents |

## 💡 How to Use This

### As a User
You can:
1. **Ask me to orchestrate** - "Use multiple agents to analyze X"
2. **Watch sessions live** - Open log files while agents work
3. **Review results** - Check transcripts and reports after completion
4. **Compare approaches** - See how different models tackle the same problem

### What I (Kiro) Can Do
I can now:
1. **Delegate to specialists** - Send code tasks to gpt-5.3-codex
2. **Parallelize work** - Run multiple analyses simultaneously
3. **Leverage strengths** - Use gpt-5.5 for research, gpt-5.3-codex-spark for quick scans
4. **Synthesize results** - Combine insights from multiple perspectives
5. **Maintain oversight** - Monitor and coordinate all agent work

## 📁 File Structure

```
.acp-sessions/
├── acp-bridge.py           # Single agent interface
├── acp-orchestrator.py     # Multi-agent coordinator
├── view-session.py         # Session viewer
├── README.md               # Full documentation
├── QUICKSTART.md          # This file
│
├── session_*.log          # Human-readable logs
├── transcript_*.jsonl     # Complete JSON-RPC logs
│
└── run_TIMESTAMP/         # Orchestration runs
    ├── orchestrator.log   # Coordination events
    ├── comparison.json    # Result comparison
    └── report.md          # Synthesized findings
```

## 🎬 Try It Now

### Test 1: Quick Analysis
```bash
python3 .acp-sessions/acp-bridge.py "$(pwd)" \
  "List the 5 most important files in JoyShockMapper/src" \
  "gpt-5.3-codex-spark"
```

### Test 2: View the Result
```bash
python3 .acp-sessions/view-session.py
```

### Test 3: Multi-Agent (takes ~2-3 minutes)
```bash
python3 .acp-sessions/acp-orchestrator.py \
  "What are the key architectural patterns in JSM?"
```

## 🔮 What This Enables

### For JSM Development
- **Architecture Analysis**: Multiple perspectives on design decisions
- **Migration Planning**: Parallel research and impact analysis
- **Code Review**: Automated multi-agent review before commits
- **Refactoring**: Coordinated changes across multiple files
- **Bug Investigation**: Parallel diagnosis from different angles

### For You
- **Transparency**: See exactly what each agent is doing
- **Control**: Monitor and intervene if needed
- **Comparison**: Evaluate different AI approaches
- **Learning**: Understand how different models think
- **Efficiency**: Parallel work instead of sequential

## 📚 Next Steps

1. **Try the examples above** to see it in action
2. **Read README.md** for detailed documentation
3. **Ask me to orchestrate** on real JSM tasks
4. **Watch sessions live** to see how agents work
5. **Review transcripts** to understand agent reasoning

## 🤝 How We Work Together

**You:** "I need to migrate the gyro handling to SDL3"

**Me (Kiro):**
1. Spawn gpt-5.5 to research SDL3 gyro APIs
2. Spawn gpt-5.4 to analyze current JSM gyro code
3. Spawn gpt-5.3-codex to draft migration approach
4. Compare all three analyses
5. Synthesize a unified migration plan
6. Present it to you with full transparency

**You:** Watch the sessions live or review after completion

**Result:** High-quality plan informed by multiple AI perspectives, fully visible to you

---

**Ready to try it?** Just ask me to orchestrate something!
