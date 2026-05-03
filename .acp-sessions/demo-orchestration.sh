#!/bin/bash
# Demo script showing ACP orchestration capabilities

echo "==================================================================="
echo "ACP Multi-Agent Orchestration Demo"
echo "==================================================================="
echo ""
echo "This demonstrates Kiro orchestrating multiple Codex agents via ACP"
echo ""

# Example 1: Single agent quick task
echo "Example 1: Quick analysis with gpt-5.3-codex-spark"
echo "-------------------------------------------------------------------"
python3 .acp-sessions/acp-bridge.py "$(pwd)" \
  "List the 5 most important C++ files in JoyShockMapper/src and explain their role in one sentence each" \
  "gpt-5.3-codex-spark"

echo ""
echo "View the session:"
echo "  python3 .acp-sessions/view-session.py"
echo ""
echo "==================================================================="
echo ""

# Example 2: Parallel analysis (commented out for speed)
# echo "Example 2: Parallel architecture analysis with 3 agents"
# echo "-------------------------------------------------------------------"
# python3 .acp-sessions/acp-orchestrator.py \
#   "Identify the key architectural patterns in JoyShockMapper"
# echo ""
# echo "View results in: .acp-sessions/run_*/report.md"
# echo ""

echo "==================================================================="
echo "Available Commands:"
echo "==================================================================="
echo ""
echo "1. Single agent task:"
echo "   python3 .acp-sessions/acp-bridge.py <workspace> <prompt> <model>"
echo ""
echo "2. Multi-agent orchestration:"
echo "   python3 .acp-sessions/acp-orchestrator.py <task>"
echo ""
echo "3. View session transcript:"
echo "   python3 .acp-sessions/view-session.py [transcript_file]"
echo ""
echo "4. Watch session live:"
echo "   tail -f .acp-sessions/session_*.log"
echo ""
echo "==================================================================="
echo "Available Models:"
echo "==================================================================="
echo ""
echo "  gpt-5.5              - Frontier model (complex tasks)"
echo "  gpt-5.4              - Strong everyday coding"
echo "  gpt-5.4-mini         - Fast and efficient"
echo "  gpt-5.3-codex        - Coding-optimized"
echo "  gpt-5.3-codex-spark  - Ultra-fast"
echo "  gpt-5.2              - Long-running agents"
echo ""
echo "==================================================================="
