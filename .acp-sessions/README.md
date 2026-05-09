# ACP Multi-Agent Orchestration for Kiro

This directory contains tools for orchestrating multiple AI coding agents via the Agent Client Protocol (ACP). It enables Kiro (Claude) to spawn and coordinate Codex agents with different models for parallel analysis, implementation, and review.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kiro (Claude Sonnet)                     │
│                  Main Orchestration Agent                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ spawns & coordinates via ACP
                     │
        ┌────────────┼────────────┬────────────────┐
        │            │            │                │
        ▼            ▼            ▼                ▼
   ┌────────┐  ┌────────┐  ┌────────┐      ┌────────┐
   │ Codex  │  │ Codex  │  │ Codex  │ ...  │ Codex  │
   │ gpt-5.5│  │ gpt-5.4│  │ gpt-5.3│      │ gpt-5.2│
   └────────┘  └────────┘  └────────┘      └────────┘
        │            │            │                │
        └────────────┴────────────┴────────────────┘
                     │
                     ▼
              Your JSM Codebase
```

## Components

### 1. `acp-bridge.py` - Single Agent Interface
Spawns a single Codex agent and manages JSON-RPC communication.

**Usage:**
```bash
python3 .acp-sessions/acp-bridge.py <workspace> <prompt> <model>
```

**Example:**
```bash
python3 .acp-sessions/acp-bridge.py "$(pwd)" \
  "Analyze the SDL3 wrapper implementation" \
  "gpt-5.4"
```

**Output:**
- `.acp-sessions/session_TIMESTAMP.log` - Human-readable event log
- `.acp-sessions/transcript_TIMESTAMP.jsonl` - Complete JSON-RPC transcript

### 2. `acp-orchestrator.py` - Multi-Agent Coordinator
Coordinates multiple agents working in parallel on complex tasks.

**Usage:**
```bash
python3 .acp-sessions/acp-orchestrator.py "task description"
```

**Example:**
```bash
python3 .acp-sessions/acp-orchestrator.py \
  "Identify refactoring opportunities in the input handling code"
```

**Features:**
- **Parallel Diagnosis**: Multiple agents analyze the same problem independently
- **Result Comparison**: Automatic comparison of agent outputs
- **Synthesis**: Combined report from all agent findings
- **Real-time Visibility**: All sessions logged to files

**Output:**
- `.acp-sessions/run_TIMESTAMP/` - Run directory containing:
  - `orchestrator.log` - Orchestration events
  - `comparison.json` - Structured comparison of results
  - `report.md` - Synthesized findings
- Individual agent session logs and transcripts

### 3. `view-session.py` - Session Viewer
Displays session transcripts in human-readable format.

**Usage:**
```bash
# View most recent session
python3 .acp-sessions/view-session.py

# View specific session
python3 .acp-sessions/view-session.py transcript_TIMESTAMP.jsonl
```

**Output Format:**
```
👤 USER: <prompt>
🤖 AGENT: <response>
🔧 TOOL CALLS:
  • <tool name> [status]
    <output preview>
✓ Session ended: <reason>
```

## Available Models

| Model | Best For | Speed | Reasoning |
|-------|----------|-------|-----------|
| `gpt-5.5` | Complex architecture, research | Slow | Highest |
| `gpt-5.4` | Everyday coding tasks | Medium | High |
| `gpt-5.4-mini` | Quick analysis, simple tasks | Fast | Medium |
| `gpt-5.3-codex` | Code-focused implementation | Medium | High |
| `gpt-5.3-codex-spark` | Ultra-fast scanning | Fastest | Low |
| `gpt-5.2` | Long-running autonomous work | Slow | High |

Each model also supports reasoning effort levels: `low`, `medium`, `high`, `xhigh`

## Orchestration Patterns

### Pattern 1: Parallel Diagnosis
Multiple agents independently analyze a problem, then results are compared.

**Use Case:** Bug investigation, architecture analysis, migration planning

**Example:**
```python
agents = [
    AgentConfig("fast-scout", "gpt-5.3-codex-spark", "low"),
    AgentConfig("deep-analyzer", "gpt-5.4", "high"),
    AgentConfig("specialist", "gpt-5.3-codex", "medium")
]
results = orchestrator.parallel_diagnosis(agents, task)
```

### Pattern 2: Specialized Roles
Assign different roles to agents based on their strengths.

**Roles:**
- **Scout**: Quick initial analysis (gpt-5.3-codex-spark)
- **Implementer**: Write code (gpt-5.3-codex, gpt-5.4)
- **Reviewer**: Check quality (gpt-5.4, gpt-5.5)
- **Researcher**: Deep investigation (gpt-5.5)

### Pattern 3: Iterative Refinement
One agent implements, another reviews, first agent refines.

**Use Case:** Complex features requiring high quality

### Pattern 4: Divide and Conquer
Split large tasks across multiple agents working on different parts.

**Use Case:** Multi-file refactoring, large feature implementation

## Real-Time Monitoring

### Watch a Session Live
```bash
# Start a task in the background
python3 .acp-sessions/acp-bridge.py "$(pwd)" "your task" "gpt-5.4" &

# Watch the log file
tail -f .acp-sessions/session_*.log
```

### Monitor Multiple Agents
```bash
# Terminal 1: Start orchestration
python3 .acp-sessions/acp-orchestrator.py "complex task"

# Terminal 2: Watch orchestrator
tail -f .acp-sessions/run_*/orchestrator.log

# Terminal 3: Watch specific agent
tail -f .acp-sessions/session_fast-scout_*.log
```

## Integration with Kiro

Kiro (Claude) can use these tools to:

1. **Delegate specialized tasks** to Codex models optimized for specific work
2. **Parallelize analysis** across multiple models simultaneously
3. **Compare approaches** from different AI perspectives
4. **Leverage model strengths** (e.g., gpt-5.5 for research, gpt-5.3-codex for implementation)
5. **Maintain oversight** while agents work autonomously

### Example Workflow

```
User: "Migrate JSM from JoyShockLibrary to SDL3"

Kiro (Claude):
  1. Spawns gpt-5.5 to research SDL3 APIs
  2. Spawns gpt-5.4 to analyze current JSL usage
  3. Spawns gpt-5.3-codex to draft migration plan
  4. Compares all three analyses
  5. Synthesizes final migration strategy
  6. Presents unified plan to user
```

## Session Files

### Session Log (`.log`)
Human-readable event stream:
```
[15:49:35.187] Starting agent: npx --yes @zed-industries/codex-acp...
[15:49:35.188] Agent started with PID 117148
[15:49:35.188] → Sending: initialize
[15:49:35.189] ← Received: response
[15:49:35.189] ✓ Initialized successfully
```

### Transcript (`.jsonl`)
Complete JSON-RPC message log (one message per line):
```json
{"timestamp": "2026-05-02T15:49:35.187", "direction": "sent", "message": {...}}
{"timestamp": "2026-05-02T15:49:35.188", "direction": "received", "message": {...}}
```

## Advanced Usage

### Custom Agent Configuration

```python
from acp_orchestrator import AgentConfig, ACPOrchestrator

# Define custom agents
agents = [
    AgentConfig(
        name="architecture-analyst",
        model="gpt-5.5",
        reasoning_effort="xhigh",
        role="architecture-review"
    ),
    AgentConfig(
        name="quick-implementer",
        model="gpt-5.3-codex-spark",
        reasoning_effort="low",
        role="rapid-prototyping"
    )
]

# Run orchestration
orchestrator = ACPOrchestrator(workspace_root, session_dir)
results = orchestrator.parallel_diagnosis(agents, task)
comparison = orchestrator.compare_results(results)
report = orchestrator.synthesize_report(results)
```

### Programmatic Access

```python
from acp_bridge import ACPAgent, AgentConfig

# Create and run agent
config = AgentConfig("my-agent", "gpt-5.4", "high")
agent = ACPAgent(config, workspace_root, session_dir)

agent.start()
agent.initialize()
agent.create_session()

result = agent.send_prompt("Analyze this code...")

agent.close_session()
agent.shutdown()
```

## Troubleshooting

### Agent Won't Start
- Check that `npx` and `@zed-industries/codex-acp` are available
- Verify authentication (OPENAI_API_KEY or ChatGPT login)
- Check session logs for error messages

### Slow Response
- Try a faster model (gpt-5.3-codex-spark, gpt-5.4-mini)
- Reduce reasoning effort level
- Simplify the prompt

### Session Timeout
- Increase timeout in code
- Break task into smaller chunks
- Use faster model for initial analysis

## ACP Protocol Details

This implementation follows the [Agent Client Protocol](https://agentclientprotocol.com/) specification:

- **Transport**: stdio (JSON-RPC over stdin/stdout)
- **Protocol Version**: 2026-01-01
- **Methods Used**:
  - `initialize` - Establish connection
  - `session/new` - Create new session
  - `session/prompt` - Send user message
  - `session/close` - Close session
- **Notifications**:
  - `session/update` - Streaming responses from agent

## Future Enhancements

- [ ] Session persistence and resume
- [ ] Worktree isolation for parallel implementations
- [ ] Automatic result validation
- [ ] Cross-agent communication
- [ ] Dynamic agent selection based on task type
- [ ] Cost tracking and optimization
- [ ] Integration with Kiro hooks for automatic orchestration

## References

- [Agent Client Protocol Docs](https://agentclientprotocol.com/)
- [Codex CLI Documentation](https://developers.openai.com/codex/cli)
- [ACP Arbiter Skill](.codex/skills/acp_arbiter.md)
