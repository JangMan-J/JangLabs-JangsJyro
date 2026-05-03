#!/usr/bin/env python3
"""
ACP Bridge - Communicate with ACP agents via JSON-RPC over stdio
Streams session output to files for real-time visibility
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class ACPBridge:
    def __init__(self, agent_command: list[str], session_dir: Path):
        self.agent_command = agent_command
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.session_dir / f"session_{self.session_id}.log"
        self.transcript_file = self.session_dir / f"transcript_{self.session_id}.jsonl"
        
        self.process: Optional[subprocess.Popen] = None
        self.message_id = 0
        
    def log(self, message: str):
        """Log to session file with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(self.session_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
        # Don't print to stderr - only log to file
    
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
    
    def start_agent(self):
        """Start the ACP agent subprocess"""
        self.log(f"Starting agent: {' '.join(self.agent_command)}")
        self.process = subprocess.Popen(
            self.agent_command,
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
        self.log(f"→ Sending: {message.get('method', 'response')}")
        self.log_jsonrpc("sent", message)
        
        self.process.stdin.write(message_str + "\n")
        self.process.stdin.flush()
    
    def receive_message(self, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Receive JSON-RPC message from agent"""
        if not self.process or not self.process.stdout:
            raise RuntimeError("Agent not started")
        
        # Read line from stdout
        line = self.process.stdout.readline()
        if not line:
            return None
        
        try:
            message = json.loads(line)
            method = message.get('method', 'response')
            self.log(f"← Received: {method}")
            self.log_jsonrpc("received", message)
            return message
        except json.JSONDecodeError as e:
            self.log(f"ERROR: Failed to parse JSON: {e}")
            self.log(f"Raw line: {line}")
            return None
    
    def initialize(self) -> Dict[str, Any]:
        """Send initialize request"""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    }
                },
                "clientInfo": {
                    "name": "kiro-acp-bridge",
                    "version": "0.1.0"
                }
            }
        }
        
        self.send_message(request)
        response = self.receive_message()
        
        if response and "result" in response:
            self.log("✓ Initialized successfully")
            return response["result"]
        else:
            self.log("✗ Initialization failed")
            return {}
    
    def create_session(self, workspace_root: str) -> str:
        """Create a new session"""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "session/new",
            "params": {
                "cwd": workspace_root,
                "mcpServers": []
            }
        }
        
        self.send_message(request)
        response = self.receive_message()
        
        if response and "result" in response:
            session_id = response["result"].get("sessionId", "")
            self.log(f"✓ Session created: {session_id}")
            return session_id
        else:
            self.log("✗ Session creation failed")
            return ""
    
    def send_prompt(self, session_id: str, prompt: str):
        """Send a prompt to the session"""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "session/prompt",
            "params": {
                "sessionId": session_id,
                "prompt": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        }
        
        self.send_message(request)
        self.log(f"Prompt sent, waiting for response...")
        
        # Collect all responses until we get the final one
        responses = []
        while True:
            response = self.receive_message(timeout=60.0)
            if not response:
                break
            
            responses.append(response)
            
            # Check if this is the final response
            if "result" in response and response.get("id") == self.message_id:
                self.log("✓ Received final response")
                break
            
            # Handle notifications (streaming updates)
            if "method" in response:
                self.log(f"  Notification: {response['method']}")
        
        return responses
    
    def close_session(self, session_id: str):
        """Close the session"""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": "session/close",
            "params": {
                "sessionId": session_id
            }
        }
        
        self.send_message(request)
        response = self.receive_message()
        
        if response:
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


def main():
    if len(sys.argv) < 4:
        print("Usage: acp-bridge.py <workspace_root> <prompt> <model>")
        print("Example: acp-bridge.py /path/to/repo 'Fix the bug' gpt-5.4")
        sys.exit(1)
    
    workspace_root = sys.argv[1]
    prompt = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "gpt-5.4"
    
    # Agent command
    agent_command = ["npx", "--yes", "@zed-industries/codex-acp", "-c", f'model="{model}"']
    
    # Create bridge
    session_dir = Path(".acp-sessions")
    bridge = ACPBridge(agent_command, session_dir)
    
    try:
        # Start agent
        bridge.start_agent()
        time.sleep(1)  # Give agent time to start
        
        # Initialize
        init_result = bridge.initialize()
        
        # Create session
        session_id = bridge.create_session(workspace_root)
        
        if session_id:
            # Send prompt
            responses = bridge.send_prompt(session_id, prompt)
            
            # Close session
            bridge.close_session(session_id)
        
        # Output session file location
        print(f"\nSession log: {bridge.session_file}")
        print(f"Transcript: {bridge.transcript_file}")
        
    except Exception as e:
        bridge.log(f"ERROR: {e}")
        import traceback
        bridge.log(traceback.format_exc())
    finally:
        bridge.shutdown()


if __name__ == "__main__":
    main()
