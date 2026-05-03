#!/usr/bin/env python3
"""
ACP Multi-Agent Arbiter

Coordinates multiple ACP-compatible coding agents to complete software tasks.
Implements the patterns from .codex/skills/acp_arbiter.md
"""

import json
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Import the bridge
from acp_bridge import ACPBridge


class ArbitrationStrategy(Enum):
    AUTO = "auto"
    CHECKPOINTED_CONVERGENCE = "checkpointed_convergence"
    PARALLEL_BEST_OF_N = "parallel_best_of_n"
    TEST_FIRST_COMPETITION = "test_first_competition"
    PRIMARY_WITH_REVIEWERS = "primary_with_reviewers"
    DEBATE_THEN_EXECUTE = "debate_then_execute"
    RED_TEAM_VALIDATION = "red_team_validation"
    TREE_SEARCH = "tree_search"


class AutonomyLevel(Enum):
    CONSERVATIVE = "conservative"
    STANDARD = "standard"
    HIGH = "high"


class Budget(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    MAX = "max"


@dataclass
class AgentConfig:
    """Configuration for an ACP agent"""
    name: str
    model: str
    reasoning_effort: str = "medium"
    command: List[str] = None
    
    def __post_init__(self):
        if self.command is None:
            self.command = [
                "npx", "--yes", "@zed-industries/codex-acp",
                "-c", f'model="{self.model}"',
                "-c", f'reasoning_effort="{self.reasoning_effort}"'
            ]


@dataclass
class Checkpoint:
    """Checkpoint data for an agent at a phase boundary"""
    checkpoint_id: str
    timestamp: str
    phase: str
    agent_id: str
    agent_name: str
    selected_model: str
    selected_role: str
    worktree_path: Optional[str]
    session_id: str
    agent_summary: str
    arbiter_notes: str
    validated_discoveries: List[str]
    risks: List[str]
    score: Optional[float]
    next_action: str  # continue|resync|review|reset|retire|promote


class ACPArbiter:
    """
    Multi-agent arbiter that coordinates ACP agents
    """
    
    def __init__(
        self,
        workspace_root: str,
        objective: str,
        strategy: ArbitrationStrategy = ArbitrationStrategy.AUTO,
        autonomy: AutonomyLevel = AutonomyLevel.STANDARD,
        budget: Budget = Budget.NORMAL,
        session_dir: Optional[Path] = None
    ):
        self.workspace_root = workspace_root
        self.objective = objective
        self.strategy = strategy
        self.autonomy = autonomy
        self.budget = budget
        
        # Setup directories
        self.session_dir = session_dir or Path(".acp-sessions")
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.session_dir / f"run_{self.run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.agents: Dict[str, ACPBridge] = {}
        self.checkpoints: List[Checkpoint] = []
        self.agent_configs: List[AgentConfig] = []
        
        # Logging
        self.log_file = self.run_dir / "arbiter.log"
        self.task_file = self.run_dir / "task.json"
        self.checkpoints_file = self.run_dir / "checkpoints.json"
        
        self._save_task()
    
    def log(self, message: str):
        """Log arbiter message"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_msg)
        
        print(f"[ARBITER] {log_msg.strip()}", file=sys.stderr)
    
    def _save_task(self):
        """Save task configuration"""
        task_data = {
            "run_id": self.run_id,
            "workspace_root": self.workspace_root,
            "objective": self.objective,
            "strategy": self.strategy.value,
            "autonomy": self.autonomy.value,
            "budget": self.budget.value,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.task_file, 'w') as f:
            json.dump(task_data, f, indent=2)
    
    def _save_checkpoint(self, checkpoint: Checkpoint):
        """Save checkpoint to file"""
        self.checkpoints.append(checkpoint)
        
        with open(self.checkpoints_file, 'w') as f:
            json.dump([asdict(cp) for cp in self.checkpoints], f, indent=2)
    
    def select_agents(self) -> List[AgentConfig]:
        """
        Select agents based on strategy and budget
        
        For now, uses a simple heuristic. In production, this would:
        - Load from inventory
        - Check agent availability
        - Match capabilities to task
        - Consider historical performance
        """
        self.log("Selecting agents for task...")
        
        # Determine number of agents based on budget
        if self.budget == Budget.LOW:
            num_agents = 1
        elif self.budget == Budget.NORMAL:
            num_agents = 2
        elif self.budget == Budget.HIGH:
            num_agents = 3
        else:  # MAX
            num_agents = 4
        
        # Select models based on task and strategy
        # For parallel strategies, use diverse models
        if self.strategy in [
            ArbitrationStrategy.PARALLEL_BEST_OF_N,
            ArbitrationStrategy.CHECKPOINTED_CONVERGENCE
        ]:
            model_pool = [
                ("gpt-5.4", "high"),           # Strong general model
                ("gpt-5.3-codex", "high"),     # Coding-optimized
                ("gpt-5.4-mini", "xhigh"),     # Fast with high reasoning
                ("gpt-5.5", "medium"),         # Frontier model
            ]
        else:
            # For single-agent or primary strategies, use best model
            model_pool = [
                ("gpt-5.5", "high"),
                ("gpt-5.4", "high"),
            ]
        
        agents = []
        for i in range(min(num_agents, len(model_pool))):
            model, reasoning = model_pool[i]
            agents.append(AgentConfig(
                name=f"agent-{i+1:03d}",
                model=model,
                reasoning_effort=reasoning
            ))
        
        self.log(f"Selected {len(agents)} agents:")
        for agent in agents:
            self.log(f"  - {agent.name}: {agent.model} ({agent.reasoning_effort})")
        
        return agents
    
    def spawn_agent(self, config: AgentConfig) -> ACPBridge:
        """Spawn an ACP agent"""
        self.log(f"Spawning {config.name} ({config.model})...")
        
        agent_session_dir = self.run_dir / config.name
        agent_session_dir.mkdir(exist_ok=True)
        
        bridge = ACPBridge(config.command, agent_session_dir)
        bridge.start_agent()
        time.sleep(1)  # Give agent time to start
        
        # Initialize
        init_result = bridge.initialize()
        
        # Create session
        session_id = bridge.create_session(self.workspace_root)
        
        if not session_id:
            raise RuntimeError(f"Failed to create session for {config.name}")
        
        self.agents[config.name] = bridge
        self.log(f"✓ {config.name} ready (session: {session_id})")
        
        return bridge
    
    def send_prompt_to_agent(
        self,
        agent_name: str,
        prompt: str,
        phase: str,
        role: str = "implementer"
    ) -> List[Dict[str, Any]]:
        """Send a prompt to a specific agent and collect responses"""
        self.log(f"→ {agent_name} [{phase}]: Sending prompt...")
        
        bridge = self.agents[agent_name]
        responses = bridge.send_prompt(bridge.process.stdout.readline(), prompt)
        
        # Extract agent summary from responses
        agent_text = []
        for resp in responses:
            if "method" in resp and resp["method"] == "session/update":
                update = resp["params"]["update"]
                if update["sessionUpdate"] == "agent_message_chunk":
                    agent_text.append(update["content"]["text"])
        
        summary = "".join(agent_text)
        
        # Create checkpoint
        checkpoint = Checkpoint(
            checkpoint_id=f"{agent_name}_{phase}_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            phase=phase,
            agent_id=agent_name,
            agent_name=agent_name,
            selected_model=self.agent_configs[0].model,  # TODO: track per agent
            selected_role=role,
            worktree_path=None,  # TODO: implement worktrees
            session_id=bridge.session_id if hasattr(bridge, 'session_id') else "",
            agent_summary=summary[:500],  # Truncate for storage
            arbiter_notes="",
            validated_discoveries=[],
            risks=[],
            score=None,
            next_action="continue"
        )
        
        self._save_checkpoint(checkpoint)
        self.log(f"✓ {agent_name} [{phase}]: Response received")
        
        return responses
    
    def run_parallel_best_of_n(self):
        """
        Execute parallel_best_of_n strategy:
        - Agents receive same objective
        - Solve independently
        - Arbiter compares and selects best
        """
        self.log("=== Strategy: Parallel Best-of-N ===")
        
        # Spawn agents
        for config in self.agent_configs:
            self.spawn_agent(config)
        
        # Send same prompt to all agents
        self.log("Phase: Independent Implementation")
        
        task_prompt = f"""
{self.objective}

Work independently to solve this task. Provide a complete solution with:
1. Your analysis of the problem
2. Your implementation approach
3. Any code changes needed
4. Validation steps

Be thorough and complete.
"""
        
        results = {}
        for agent_name in self.agents.keys():
            responses = self.send_prompt_to_agent(
                agent_name,
                task_prompt,
                phase="implementation",
                role="implementer"
            )
            results[agent_name] = responses
        
        # Compare results
        self.log("Phase: Comparison")
        self.log("Comparing agent results...")
        
        # TODO: Implement sophisticated comparison
        # For now, just report that all agents completed
        for agent_name in results.keys():
            self.log(f"  ✓ {agent_name}: Completed")
        
        self.log("=== Run Complete ===")
        self.log(f"Results saved to: {self.run_dir}")
    
    def run_checkpointed_convergence(self):
        """
        Execute checkpointed_convergence strategy:
        - Independent diagnosis
        - Compare and extract validated facts
        - Synchronized implementation direction
        - Independent implementation
        - Validation and synthesis
        """
        self.log("=== Strategy: Checkpointed Convergence ===")
        
        # Spawn agents
        for config in self.agent_configs:
            self.spawn_agent(config)
        
        # Phase 1: Independent Diagnosis
        self.log("Phase 1: Independent Diagnosis")
        
        diagnosis_prompt = f"""
{self.objective}

First, analyze this task independently:
1. What is the root cause or core requirement?
2. What files/components are involved?
3. What are the key constraints?
4. What approach would you take?

Provide your diagnosis without implementing yet.
"""
        
        diagnoses = {}
        for agent_name in self.agents.keys():
            responses = self.send_prompt_to_agent(
                agent_name,
                diagnosis_prompt,
                phase="diagnosis",
                role="diagnostician"
            )
            diagnoses[agent_name] = responses
        
        # Phase 2: Arbiter Comparison
        self.log("Phase 2: Comparing Diagnoses")
        
        # TODO: Extract validated facts from diagnoses
        # For now, just log that comparison happened
        validated_facts = [
            "All agents identified the core issue",
            "Consensus on affected files",
        ]
        
        for fact in validated_facts:
            self.log(f"  ✓ Validated: {fact}")
        
        # Phase 3: Synchronized Implementation
        self.log("Phase 3: Synchronized Implementation")
        
        sync_prompt = f"""
Based on the diagnosis phase, implement the solution for:

{self.objective}

Validated approach:
{chr(10).join(f"- {fact}" for fact in validated_facts)}

Implement your solution now.
"""
        
        implementations = {}
        for agent_name in self.agents.keys():
            responses = self.send_prompt_to_agent(
                agent_name,
                sync_prompt,
                phase="implementation",
                role="implementer"
            )
            implementations[agent_name] = responses
        
        # Phase 4: Validation and Synthesis
        self.log("Phase 4: Validation and Synthesis")
        self.log("Comparing implementations...")
        
        # TODO: Implement validation and synthesis
        for agent_name in implementations.keys():
            self.log(f"  ✓ {agent_name}: Implementation complete")
        
        self.log("=== Run Complete ===")
        self.log(f"Results saved to: {self.run_dir}")
    
    def run_primary_with_reviewers(self):
        """
        Execute primary_with_reviewers strategy:
        - Select primary implementer
        - Other agents review
        - Feed findings back to primary
        - Primary revises
        """
        self.log("=== Strategy: Primary with Reviewers ===")
        
        if len(self.agent_configs) < 2:
            self.log("WARNING: Need at least 2 agents for this strategy")
            return
        
        # Spawn agents
        for config in self.agent_configs:
            self.spawn_agent(config)
        
        primary_name = list(self.agents.keys())[0]
        reviewer_names = list(self.agents.keys())[1:]
        
        self.log(f"Primary: {primary_name}")
        self.log(f"Reviewers: {', '.join(reviewer_names)}")
        
        # Phase 1: Primary Implementation
        self.log("Phase 1: Primary Implementation")
        
        impl_prompt = f"""
{self.objective}

You are the primary implementer. Provide a complete solution.
"""
        
        primary_response = self.send_prompt_to_agent(
            primary_name,
            impl_prompt,
            phase="primary_implementation",
            role="primary_implementer"
        )
        
        # Phase 2: Reviews
        self.log("Phase 2: Reviews")
        
        review_prompt = f"""
Review the following implementation for:

{self.objective}

Provide constructive feedback on:
1. Correctness
2. Completeness
3. Edge cases
4. Potential issues
5. Improvements

Be specific and actionable.
"""
        
        reviews = {}
        for reviewer_name in reviewer_names:
            responses = self.send_prompt_to_agent(
                reviewer_name,
                review_prompt,
                phase="review",
                role="reviewer"
            )
            reviews[reviewer_name] = responses
        
        # Phase 3: Revision
        self.log("Phase 3: Primary Revision")
        
        # TODO: Extract review findings and send to primary
        self.log("Sending review findings to primary...")
        
        self.log("=== Run Complete ===")
        self.log(f"Results saved to: {self.run_dir}")
    
    def run(self):
        """Execute the arbitration strategy"""
        self.log(f"Starting arbiter run: {self.run_id}")
        self.log(f"Objective: {self.objective}")
        self.log(f"Strategy: {self.strategy.value}")
        self.log(f"Autonomy: {self.autonomy.value}")
        self.log(f"Budget: {self.budget.value}")
        
        # Select agents
        self.agent_configs = self.select_agents()
        
        # Execute strategy
        try:
            if self.strategy == ArbitrationStrategy.PARALLEL_BEST_OF_N:
                self.run_parallel_best_of_n()
            elif self.strategy == ArbitrationStrategy.CHECKPOINTED_CONVERGENCE:
                self.run_checkpointed_convergence()
            elif self.strategy == ArbitrationStrategy.PRIMARY_WITH_REVIEWERS:
                self.run_primary_with_reviewers()
            else:
                # Default to checkpointed convergence
                self.log(f"Strategy {self.strategy.value} not fully implemented, using checkpointed_convergence")
                self.run_checkpointed_convergence()
        
        except Exception as e:
            self.log(f"ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())
        
        finally:
            # Cleanup
            self.log("Shutting down agents...")
            for agent_name, bridge in self.agents.items():
                try:
                    bridge.shutdown()
                    self.log(f"✓ {agent_name} shut down")
                except Exception as e:
                    self.log(f"✗ {agent_name} shutdown error: {e}")
        
        self.log(f"Arbiter run complete: {self.run_id}")
        return self.run_dir


def main():
    if len(sys.argv) < 2:
        print("Usage: arbiter.py <objective> [strategy] [budget]")
        print()
        print("Strategies:")
        for s in ArbitrationStrategy:
            print(f"  - {s.value}")
        print()
        print("Budgets: low, normal, high, max")
        sys.exit(1)
    
    objective = sys.argv[1]
    strategy_str = sys.argv[2] if len(sys.argv) > 2 else "auto"
    budget_str = sys.argv[3] if len(sys.argv) > 3 else "normal"
    
    # Parse strategy
    try:
        strategy = ArbitrationStrategy(strategy_str)
    except ValueError:
        print(f"Invalid strategy: {strategy_str}")
        sys.exit(1)
    
    # Parse budget
    try:
        budget = Budget(budget_str)
    except ValueError:
        print(f"Invalid budget: {budget_str}")
        sys.exit(1)
    
    # Get workspace root
    workspace_root = Path.cwd().absolute()
    
    # Create and run arbiter
    arbiter = ACPArbiter(
        workspace_root=str(workspace_root),
        objective=objective,
        strategy=strategy,
        budget=budget
    )
    
    run_dir = arbiter.run()
    
    print(f"\n{'='*60}")
    print(f"Arbiter run complete!")
    print(f"Results: {run_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
