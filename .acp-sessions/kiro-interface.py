#!/usr/bin/env python3
"""
Kiro Interface for ACP Agents
High-level functions for Kiro to use when orchestrating agents
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

class ACPInterface:
    """Clean interface for Kiro to spawn and coordinate ACP agents"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.wrapper_script = Path(workspace_root) / ".acp-sessions" / "kiro-acp-wrapper.py"
    
    def ask_agent(self, prompt: str, model: str = "gpt-5.4") -> Dict[str, Any]:
        """
        Ask a single Codex agent a question
        
        Args:
            prompt: The question or task for the agent
            model: Which Codex model to use
        
        Returns:
            {
                "success": bool,
                "response": str,  # Agent's response
                "tool_calls": list,  # Tools the agent used
                "session_file": str,  # Path to session log
                "transcript_file": str  # Path to full transcript
            }
        """
        result = subprocess.run(
            [
                sys.executable,
                str(self.wrapper_script),
                "single",
                self.workspace_root,
                prompt,
                model
            ],
            capture_output=True,
            text=True
        )
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse response",
                "raw_output": result.stdout,
                "stderr": result.stderr
            }
    
    def orchestrate(self, task: str) -> Dict[str, Any]:
        """
        Orchestrate multiple agents on a complex task
        
        Args:
            task: The complex task to coordinate agents on
        
        Returns:
            {
                "success": bool,
                "run_dir": str,  # Directory with all results
                "comparison": dict,  # Comparison of agent results
                "report": str  # Markdown report synthesizing findings
            }
        """
        result = subprocess.run(
            [
                sys.executable,
                str(self.wrapper_script),
                "orchestrate",
                self.workspace_root,
                task
            ],
            capture_output=True,
            text=True
        )
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse response",
                "raw_output": result.stdout,
                "stderr": result.stderr
            }
    
    def quick_scan(self, prompt: str) -> str:
        """Quick scan with fastest model - returns just the response text"""
        result = self.ask_agent(prompt, "gpt-5.3-codex-spark")
        return result.get("response", "") if result.get("success") else f"Error: {result.get('error')}"
    
    def deep_analysis(self, prompt: str) -> str:
        """Deep analysis with high reasoning - returns just the response text"""
        result = self.ask_agent(prompt, "gpt-5.4")
        return result.get("response", "") if result.get("success") else f"Error: {result.get('error')}"
    
    def research(self, prompt: str) -> str:
        """Research with frontier model - returns just the response text"""
        result = self.ask_agent(prompt, "gpt-5.5")
        return result.get("response", "") if result.get("success") else f"Error: {result.get('error')}"


# Convenience functions for direct use
def ask_codex(prompt: str, model: str = "gpt-5.4", workspace: Optional[str] = None) -> str:
    """
    Simple function to ask Codex a question
    
    Usage:
        response = ask_codex("What is the main entry point?")
        response = ask_codex("Analyze the SDL wrapper", model="gpt-5.5")
    """
    if workspace is None:
        workspace = str(Path.cwd())
    
    interface = ACPInterface(workspace)
    result = interface.ask_agent(prompt, model)
    
    if result.get("success"):
        return result["response"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def quick_scan(prompt: str, workspace: Optional[str] = None) -> str:
    """Quick scan with gpt-5.3-codex-spark"""
    if workspace is None:
        workspace = str(Path.cwd())
    return ACPInterface(workspace).quick_scan(prompt)


def deep_analysis(prompt: str, workspace: Optional[str] = None) -> str:
    """Deep analysis with gpt-5.4"""
    if workspace is None:
        workspace = str(Path.cwd())
    return ACPInterface(workspace).deep_analysis(prompt)


def research(prompt: str, workspace: Optional[str] = None) -> str:
    """Research with gpt-5.5"""
    if workspace is None:
        workspace = str(Path.cwd())
    return ACPInterface(workspace).research(prompt)


def orchestrate(task: str, workspace: Optional[str] = None) -> Dict[str, Any]:
    """
    Orchestrate multiple agents on a complex task
    
    Usage:
        result = orchestrate("Analyze the architecture")
        print(result["report"])
    """
    if workspace is None:
        workspace = str(Path.cwd())
    return ACPInterface(workspace).orchestrate(task)


if __name__ == "__main__":
    # Demo usage
    if len(sys.argv) < 2:
        print("Usage: kiro-interface.py <prompt>")
        print("\nExample:")
        print("  python3 .acp-sessions/kiro-interface.py 'What is the main entry point?'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    response = ask_codex(prompt)
    print(response)
