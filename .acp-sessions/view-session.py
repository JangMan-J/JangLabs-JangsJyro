#!/usr/bin/env python3
"""
View ACP session transcript in a human-readable format
"""

import json
import sys
from pathlib import Path

def view_session(transcript_file: Path):
    """Parse and display session transcript"""
    
    print(f"=== ACP Session Transcript: {transcript_file.name} ===\n")
    
    agent_message = []
    tool_calls = {}
    
    with open(transcript_file) as f:
        for line in f:
            entry = json.loads(line)
            message = entry["message"]
            
            # Skip sent messages for readability
            if entry["direction"] == "sent":
                method = message.get("method", "response")
                if method == "session/prompt":
                    prompt_text = message["params"]["prompt"][0]["text"]
                    print(f"👤 USER: {prompt_text}\n")
                continue
            
            # Handle received messages
            if "method" in message and message["method"] == "session/update":
                update = message["params"]["update"]
                update_type = update["sessionUpdate"]
                
                if update_type == "agent_message_chunk":
                    # Collect agent message chunks
                    text = update["content"]["text"]
                    agent_message.append(text)
                
                elif update_type == "tool_call":
                    # New tool call
                    tool_id = update["toolCallId"]
                    tool_calls[tool_id] = {
                        "title": update.get("title", "Unknown"),
                        "status": update["status"],
                        "output": None
                    }
                
                elif update_type == "tool_call_update":
                    # Tool call update
                    tool_id = update["toolCallId"]
                    if tool_id in tool_calls:
                        tool_calls[tool_id]["status"] = update["status"]
                        if "rawOutput" in update:
                            stdout = update["rawOutput"].get("stdout", "")
                            tool_calls[tool_id]["output"] = stdout
            
            # Handle final response
            elif "result" in message:
                # Print accumulated agent message
                if agent_message:
                    full_message = "".join(agent_message)
                    print(f"🤖 AGENT: {full_message}\n")
                    agent_message = []
                
                # Print tool calls
                if tool_calls:
                    print("🔧 TOOL CALLS:")
                    for tool_id, info in tool_calls.items():
                        print(f"  • {info['title']} [{info['status']}]")
                        if info['output']:
                            # Show first few lines of output
                            lines = info['output'].strip().split('\n')
                            for line in lines[:10]:
                                print(f"    {line}")
                            if len(lines) > 10:
                                print(f"    ... ({len(lines) - 10} more lines)")
                    print()
                    tool_calls = {}
                
                # Print stop reason
                if "stopReason" in message["result"]:
                    print(f"✓ Session ended: {message['result']['stopReason']}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Find most recent transcript
        session_dir = Path(".acp-sessions")
        transcripts = sorted(session_dir.glob("transcript_*.jsonl"))
        if not transcripts:
            print("No transcripts found")
            sys.exit(1)
        transcript_file = transcripts[-1]
    else:
        transcript_file = Path(sys.argv[1])
    
    view_session(transcript_file)
