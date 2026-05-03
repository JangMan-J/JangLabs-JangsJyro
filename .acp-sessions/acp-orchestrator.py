#!/usr/bin/env python3
"""
ACP Orchestrator - Coordinate multiple ACP agents for complex tasks

Implements patterns from the ACP Multi-Agent Arbiter skill:
- Parallel diagnosis
- Independent implementation
- Cross-review
- Result synthesis
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import threading
import queue

@dataclass
class AgentConfig:
    """Configuration for an ACP agent"""
    name: str
    model: str
    reasoning_effort: str = "medium"
    role: str = "implementer"
    
    def get_command(self) -> List[str]:
        """Get the command to spawn this agent"""
        return [
            "npx", "--yes", "@zed-industries/codex-acp",
            "-c", f'model="{self.model}"',
            "-c", f'reasoning_effort="{self.reasoning_effort}"'
        ]

@dataclass
class TaskResult:
    """Result from an agent task"""
    agent_name: str
    success: bool
    response: str
    tool_calls: List[Dict[str, Any]]
    duration: float
    session_file: Path
    transcript_file: Path

class ACPAgent:
    """Wrapper for a single ACP agent process"""
    
    def __init__(self, config: AgentConfig, workspace_root: str, session_dir: Path):
        self.config = config
        self.workspace_root = workspace_root
        self.session_dir = session_dir
        
        # Create session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{config.name}_{timestamp}"
        self.session_file = session_dir / f"session_{self.session_id}.log"
        self.transcript_file = session_dir / f"transcript_{self.session_id}.jsonl"
        
        self.process: Optional[subprocess.Popen] = None
        self.message_id = 0
        self.acp_session_id: Optional[str] = None
        
    def log(self, message: str):
        """Log to session file with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(self.session_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    
    def log_jsonrpc(self, direction: str, message: Dict[str, Any]):
        """Log JSON-RPC message to transcript"""
        with open(self.transcript_file, 'a') as f:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "direction": direction,
                "message": message
            }
            f.write(json.dumps(entry) + "\n")
            f.flush()
    
    def start(self):
        """Start the agent subprocess"""
        command = self.config.get_command()
        self.log(f"Starting {self.config.name} ({self.config.model})")
        self.log(f"Role: {self.config.role}")
        self.log(f"Command: {' '.join(command)}")
        
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.log(f"Agent started with PID {self.process.pid}")
    
    def send_message(self, message: Dict[str, Any]):
        """Send JSON-RPC message to agent"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Agent not started")
        
        message_str = json.dumps(message)
        self.log_jsonrpc("sent", message)
        self.process.stdin.write(message_str + "\n")
        self.process.stdin.flush()
    
    def receive_message(self, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Receive JSON-RPC message from agent"""
        if not self.process or not self.process.stdout:
            raise RuntimeError("Agent not started")
        
        line = self.process.stdout.readline()
        if not line:
            return None
        
        try:
            message = json.loads(line)
            self.log_jsonrpc("received", message)
            return message
        except json.JSONDecodeError as e:
            self.log(f"ERROR: Failed to parse JSON: {e}")
            return None
    
    def initialize(self) -> bool:
        """Initialize the agent"""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "kiro-acp-orchestrator", "version": "0.1.0"}
            }
        }
        
        self.send_message(request)
        response = self.receive_message()
        
        if response and "result" in response:
            self.log("✓ Initialized")
            return True
        else:
            self.log("✗ Initialization failed")
            return False
    
    def create_session(self) -> bool:
        """Create a new session"""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "session/new",
            "params": {
                "cwd": self.workspace_root,
                "mcpServers": []
            }
        }
        
        self.send_message(request)
        response = self.receive_message()
        
        if response and "result" in response:
            self.acp_session_id = response["result"].get("sessionId", "")
            self.log(f"✓ Session created: {self.acp_session_id}")
            return True
        else:
            self.log("✗ Session creation failed")
            return False
    
    def send_prompt(self, prompt: str, timeout: float = 120.0) -> TaskResult:
        """Send a prompt and collect all responses"""
        start_time = time.time()
        
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "session/prompt",
            "params": {
                "sessionId": self.acp_session_id,
                "prompt": [{"type": "text", "text": prompt}]
            }
        }
        
        self.send_message(request)
        self.log(f"Prompt sent, waiting for response...")
        
        # Collect responses
        agent_message = []
        tool_calls = []
        
        while True:
            response = self.receive_message(timeout=timeout)
            if not response:
                break
            
            # Handle notifications
            if "method" in response and response["method"] == "session/update":
                update = response["params"]["update"]
                update_type = update["sessionUpdate"]
                
                if update_type == "agent_message_chunk":
                    agent_message.append(update["content"]["text"])
                
                elif update_type == "tool_call":
                    tool_calls.append({
                        "id": update["toolCallId"],
                        "title": update.get("title", "Unknown"),
                        "status": update["status"]
                    })
                
                elif update_type == "tool_call_update":
                    # Update tool call status
                    tool_id = update["toolCallId"]
                    for tc in tool_calls:
                        if tc["id"] == tool_id:
                            tc["status"] = update["status"]
                            if "rawOutput" in update:
                                tc["output"] = update["rawOutput"].get("stdout", "")
            
            # Check for final response
            if "result" in response and response.get("id") == self.message_id:
                self.log("✓ Received final response")
                break
        
        duration = time.time() - start_time
        full_response = "".join(agent_message)
        
        self.log(f"Task completed in {duration:.1f}s")
        
        return TaskResult(
            agent_name=self.config.name,
            success=True,
            response=full_response,
            tool_calls=tool_calls,
            duration=duration,
            session_file=self.session_file,
            transcript_file=self.transcript_file
        )
    
    def close_session(self):
        """Close the session"""
        if not self.acp_session_id:
            return
        
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "session/close",
            "params": {"sessionId": self.acp_session_id}
        }
        
        self.send_message(request)
        self.receive_message()
        self.log("✓ Session closed")
    
    def shutdown(self):
        """Shutdown the agent"""
        if self.process:
            self.log("Shutting down agent...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.log("Agent shut down")


class ACPOrchestrator:
    """Orchestrate multiple ACP agents"""
    
    def __init__(self, workspace_root: str, session_dir: Path):
        self.workspace_root = workspace_root
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create run directory
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = session_dir / f"run_{self.run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.run_dir / "orchestrator.log"
    
    def log(self, message: str):
        """Log orchestrator events"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_msg)
            f.flush()
        # Don't print to stderr - only log to file
    
    def run_agent_task(self, config: AgentConfig, prompt: str) -> TaskResult:
        """Run a single agent on a task"""
        agent = ACPAgent(config, self.workspace_root, self.session_dir)
        
        try:
            agent.start()
            time.sleep(1)  # Give agent time to start
            
            if not agent.initialize():
                raise RuntimeError("Failed to initialize agent")
            
            if not agent.create_session():
                raise RuntimeError("Failed to create session")
            
            result = agent.send_prompt(prompt)
            agent.close_session()
            
            return result
            
        except Exception as e:
            agent.log(f"ERROR: {e}")
            return TaskResult(
                agent_name=config.name,
                success=False,
                response=str(e),
                tool_calls=[],
                duration=0,
                session_file=agent.session_file,
                transcript_file=agent.transcript_file
            )
        finally:
            agent.shutdown()
    
    def parallel_diagnosis(self, agents: List[AgentConfig], task: str) -> List[TaskResult]:
        """Run multiple agents in parallel for diagnosis"""
        self.log(f"=== PARALLEL DIAGNOSIS ===")
        self.log(f"Task: {task}")
        self.log(f"Agents: {', '.join(a.name for a in agents)}")
        
        # Run agents in parallel using threads
        results = []
        threads = []
        result_queue = queue.Queue()
        
        def run_agent(config: AgentConfig):
            result = self.run_agent_task(config, task)
            result_queue.put(result)
        
        # Start all agents
        for agent_config in agents:
            thread = threading.Thread(target=run_agent, args=(agent_config,))
            thread.start()
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        while not result_queue.empty():
            results.append(result_queue.get())
        
        self.log(f"✓ All agents completed")
        return results
    
    def compare_results(self, results: List[TaskResult]) -> Dict[str, Any]:
        """Compare results from multiple agents"""
        self.log(f"=== COMPARING RESULTS ===")
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "agents": [],
            "summary": {}
        }
        
        for result in results:
            agent_data = {
                "name": result.agent_name,
                "success": result.success,
                "duration": result.duration,
                "response_length": len(result.response),
                "tool_calls_count": len(result.tool_calls),
                "session_file": str(result.session_file),
                "transcript_file": str(result.transcript_file)
            }
            comparison["agents"].append(agent_data)
            
            self.log(f"  {result.agent_name}: {result.duration:.1f}s, "
                    f"{len(result.response)} chars, {len(result.tool_calls)} tools")
        
        # Save comparison
        comparison_file = self.run_dir / "comparison.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        self.log(f"✓ Comparison saved to {comparison_file}")
        return comparison
    
    def synthesize_report(self, results: List[TaskResult]) -> str:
        """Generate a synthesis report"""
        report_lines = [
            f"# ACP Orchestration Report",
            f"Run ID: {self.run_id}",
            f"Timestamp: {datetime.now().isoformat()}",
            f"",
            f"## Agents",
            ""
        ]
        
        for result in results:
            report_lines.extend([
                f"### {result.agent_name}",
                f"- Duration: {result.duration:.1f}s",
                f"- Success: {result.success}",
                f"- Tool calls: {len(result.tool_calls)}",
                f"- Session: `{result.session_file.name}`",
                f"",
                f"**Response:**",
                f"```",
                result.response[:500] + ("..." if len(result.response) > 500 else ""),
                f"```",
                f""
            ])
        
        report = "\n".join(report_lines)
        
        # Save report
        report_file = self.run_dir / "report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.log(f"✓ Report saved to {report_file}")
        return report


def main():
    if len(sys.argv) < 2:
        print("Usage: acp-orchestrator.py <task_description>")
        print("\nExample:")
        print("  acp-orchestrator.py 'Analyze the SDL3 migration requirements for JSM'")
        sys.exit(1)
    
    task = sys.argv[1]
    workspace_root = Path.cwd()
    session_dir = Path(".acp-sessions")
    
    # Create orchestrator
    orchestrator = ACPOrchestrator(str(workspace_root), session_dir)
    
    # Define agent configurations
    agents = [
        AgentConfig(
            name="fast-scout",
            model="gpt-5.3-codex-spark",
            reasoning_effort="low",
            role="quick-analysis"
        ),
        AgentConfig(
            name="deep-analyzer",
            model="gpt-5.4",
            reasoning_effort="high",
            role="detailed-analysis"
        ),
        AgentConfig(
            name="specialist",
            model="gpt-5.3-codex",
            reasoning_effort="medium",
            role="implementation-focus"
        )
    ]
    
    # Run parallel diagnosis
    results = orchestrator.parallel_diagnosis(agents, task)
    
    # Compare results
    comparison = orchestrator.compare_results(results)
    
    # Generate report
    report = orchestrator.synthesize_report(results)
    
    print(f"\n{'='*60}")
    print(f"Orchestration complete!")
    print(f"Run directory: {orchestrator.run_dir}")
    print(f"{'='*60}\n")
    
    # Print summary
    for result in results:
        print(f"{result.agent_name}:")
        print(f"  View session: python3 .acp-sessions/view-session.py {result.transcript_file}")
        print()


if __name__ == "__main__":
    main()
