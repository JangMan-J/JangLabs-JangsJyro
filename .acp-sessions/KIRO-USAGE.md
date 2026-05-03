# Using ACP Agents from Kiro

## ✅ Problem Solved

The ACP agents now run **completely isolated** from your Kiro terminal. No more output pollution!

## 🎯 Clean Interface

I've created a clean Python interface that:
- ✅ Runs agents silently in the background
- ✅ Returns only structured JSON results
- ✅ Logs everything to files for later review
- ✅ No terminal pollution whatsoever

## 🚀 How I Use It

### Method 1: Python Interface (Recommended)

```python
from pathlib import Path
import sys
sys.path.append(str(Path.cwd() / ".acp-sessions"))
from kiro_interface import ask_codex, quick_scan, deep_analysis, research, orchestrate

# Quick scan (fastest)
response = quick_scan("What files handle input in JSM?")

# Standard query
response = ask_codex("Explain the SDL wrapper architecture")

# Deep analysis
response = deep_analysis("Analyze the gyro calibration algorithm")

# Research (frontier model)
response = research("What are the best practices for SDL3 migration?")

# Multi-agent orchestration
result = orchestrate("Identify refactoring opportunities in input handling")
print(result["report"])
```

### Method 2: Command Line Wrapper

```bash
# Single agent
python3 .acp-sessions/kiro-acp-wrapper.py single "$(pwd)" \
  "What is the main entry point?" \
  "gpt-5.4"

# Returns clean JSON:
{
  "success": true,
  "response": "...",
  "tool_calls": [...],
  "session_file": "...",
  "transcript_file": "..."
}
```

### Method 3: Direct Interface

```bash
# Simple usage
python3 .acp-sessions/kiro-interface.py "What language is JSM written in?"

# Returns just the response text (no JSON wrapper)
```

## 📊 Monitoring (Optional)

If you want to watch what's happening:

```bash
# In a separate terminal
tail -f .acp-sessions/session_*.log
```

But this is **completely optional** - the agents run silently and you only see results.

## 🎨 Usage Patterns

### Pattern 1: Quick Information Gathering

```python
# I need quick facts
response = quick_scan("List the main C++ source files")
```

### Pattern 2: Code Analysis

```python
# I need detailed analysis
response = deep_analysis("Analyze the button state machine implementation")
```

### Pattern 3: Research & Planning

```python
# I need to research something
response = research("What are the SDL3 gyro APIs and how do they differ from JSL?")
```

### Pattern 4: Multi-Agent Coordination

```python
# Complex task requiring multiple perspectives
result = orchestrate("Design a migration plan from JoyShockLibrary to SDL3")

# Result contains:
# - comparison: How each agent approached it
# - report: Synthesized findings in markdown
# - run_dir: Where all session logs are stored
```

## 🔍 Reviewing Sessions

All sessions are logged to files:

```bash
# View most recent session
python3 .acp-sessions/view-session.py

# View specific session
python3 .acp-sessions/view-session.py .acp-sessions/transcript_TIMESTAMP.jsonl

# View orchestration report
cat .acp-sessions/run_TIMESTAMP/report.md
```

## 💡 Example Workflow

**You:** "I need to understand how JSM handles gyro input"

**Me (Kiro):**
```python
# Step 1: Quick scan to find relevant files
files = quick_scan("What files handle gyro input in JSM?")

# Step 2: Deep analysis of the implementation
analysis = deep_analysis(f"Analyze the gyro handling in these files: {files}")

# Step 3: Present findings to you
```

**Result:** You see only my final summary, but all agent work is logged for review.

## 🎯 Benefits

### For You
- ✅ **Clean terminal** - No output pollution
- ✅ **Fast responses** - I can delegate and continue working
- ✅ **Full transparency** - Everything logged for review
- ✅ **Optional monitoring** - Watch sessions if you want

### For Me (Kiro)
- ✅ **Parallel work** - Spawn multiple agents simultaneously
- ✅ **Model selection** - Use the right model for each task
- ✅ **Delegation** - Offload specialized work to Codex
- ✅ **Synthesis** - Combine insights from multiple agents

## 📁 File Organization

```
.acp-sessions/
├── kiro-interface.py       # ← I use this (high-level)
├── kiro-acp-wrapper.py     # ← Clean JSON wrapper
├── acp-bridge.py           # ← Low-level single agent
├── acp-orchestrator.py     # ← Low-level multi-agent
├── view-session.py         # ← You use this to review
│
├── session_*.log           # ← Silent logs (no terminal output)
├── transcript_*.jsonl      # ← Complete message logs
│
└── run_*/                  # ← Orchestration results
    ├── orchestrator.log
    ├── comparison.json
    └── report.md
```

## 🔧 Configuration

All agents run with:
- **No terminal output** - Everything goes to log files
- **Structured results** - JSON or plain text responses
- **Background execution** - Doesn't block Kiro
- **Full logging** - Every message captured for review

## 🎬 Try It Now

```bash
# Test the clean interface
python3 .acp-sessions/kiro-interface.py "What is JSM?"
```

You should see only the agent's response - no debug output, no progress messages, completely clean!

## 🤝 How We Work Together Now

**You:** "Analyze the SDL wrapper"

**Me (Kiro):**
```python
# Silently spawn agent
response = deep_analysis("Analyze the SDL wrapper architecture in JSM")

# Present clean result to you
```

**You see:** Only my formatted response with the analysis

**Behind the scenes:** 
- Agent spawned
- Session logged to `.acp-sessions/session_*.log`
- Full transcript saved to `.acp-sessions/transcript_*.jsonl`
- You can review later if interested

**Your terminal:** Completely clean! ✨

---

**The key difference:** Everything now runs in isolated subprocesses with output redirected to files. Your Kiro terminal stays pristine!
