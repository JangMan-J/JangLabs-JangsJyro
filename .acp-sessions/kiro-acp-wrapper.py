#!/usr/bin/env python3
"""
Kiro ACP Wrapper - Silent execution with clean output
Runs ACP agents in the background without terminal pollution
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_single_agent(workspace: str, prompt: str, model: str) -> dict:
    """Run a single agent and return structured result"""
    
    # Run bridge script with all output redirected
    result = subprocess.run(
        [
            sys.executable,
            ".acp-sessions/acp-bridge.py",
            workspace,
            prompt,
            model
        ],
        capture_output=True,
        text=True,
        cwd=workspace
    )
    
    # Parse the output to find session files
    session_file = None
    transcript_file = None
    
    for line in result.stdout.split('\n'):
        if 'Session log:' in line:
            session_file = line.split('Session log:')[1].strip()
        elif 'Transcript:' in line:
            transcript_file = line.split('Transcript:')[1].strip()
    
    if not transcript_file:
        return {
            "success": False,
            "error": "Failed to create session",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    # Extract agent response from transcript
    transcript_path = Path(workspace) / transcript_file
    agent_response = []
    tool_calls = []
    
    try:
        with open(transcript_path) as f:
            for line in f:
                entry = json.loads(line)
                if entry["direction"] == "received" and "method" in entry["message"]:
                    msg = entry["message"]
                    if msg["method"] == "session/update":
                        update = msg["params"]["update"]
                        if update["sessionUpdate"] == "agent_message_chunk":
                            agent_response.append(update["content"]["text"])
                        elif update["sessionUpdate"] == "tool_call":
                            tool_calls.append(update.get("title", "Unknown tool"))
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse transcript: {e}",
            "transcript_file": str(transcript_path)
        }
    
    return {
        "success": True,
        "model": model,
        "response": "".join(agent_response),
        "tool_calls": tool_calls,
        "session_file": session_file,
        "transcript_file": transcript_file
    }

def run_orchestration(workspace: str, task: str) -> dict:
    """Run multi-agent orchestration and return structured result"""
    
    # Run orchestrator with all output redirected
    result = subprocess.run(
        [
            sys.executable,
            ".acp-sessions/acp-orchestrator.py",
            task
        ],
        capture_output=True,
        text=True,
        cwd=workspace
    )
    
    # Find the run directory
    session_dir = Path(workspace) / ".acp-sessions"
    run_dirs = sorted(session_dir.glob("run_*"))
    
    if not run_dirs:
        return {
            "success": False,
            "error": "No run directory created",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    run_dir = run_dirs[-1]
    
    # Read comparison and report
    comparison_file = run_dir / "comparison.json"
    report_file = run_dir / "report.md"
    
    comparison = None
    report = None
    
    if comparison_file.exists():
        with open(comparison_file) as f:
            comparison = json.load(f)
    
    if report_file.exists():
        with open(report_file) as f:
            report = f.read()
    
    return {
        "success": True,
        "run_dir": str(run_dir),
        "comparison": comparison,
        "report": report
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: kiro-acp-wrapper.py <mode> [args...]"
        }))
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "single":
        if len(sys.argv) < 5:
            print(json.dumps({
                "success": False,
                "error": "Usage: kiro-acp-wrapper.py single <workspace> <prompt> <model>"
            }))
            sys.exit(1)
        
        workspace = sys.argv[2]
        prompt = sys.argv[3]
        model = sys.argv[4]
        
        result = run_single_agent(workspace, prompt, model)
        print(json.dumps(result, indent=2))
    
    elif mode == "orchestrate":
        if len(sys.argv) < 4:
            print(json.dumps({
                "success": False,
                "error": "Usage: kiro-acp-wrapper.py orchestrate <workspace> <task>"
            }))
            sys.exit(1)
        
        workspace = sys.argv[2]
        task = sys.argv[3]
        
        result = run_orchestration(workspace, task)
        print(json.dumps(result, indent=2))
    
    else:
        print(json.dumps({
            "success": False,
            "error": f"Unknown mode: {mode}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
