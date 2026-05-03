#!/usr/bin/env python3
"""
High-level orchestration interface for Kiro to use
"""

import sys
import json
from pathlib import Path
from arbiter import ACPArbiter, ArbitrationStrategy, Budget, AutonomyLevel


def orchestrate(
    objective: str,
    strategy: str = "auto",
    budget: str = "normal",
    workspace: str = None
) -> dict:
    """
    Orchestrate multiple ACP agents to complete a task
    
    Returns a summary dict with:
    - run_dir: Path to results
    - agents_used: List of agent names
    - strategy: Strategy used
    - status: success/partial/failed
    """
    
    # Parse inputs
    try:
        strat = ArbitrationStrategy(strategy)
    except ValueError:
        strat = ArbitrationStrategy.AUTO
    
    try:
        budg = Budget(budget)
    except ValueError:
        budg = Budget.NORMAL
    
    workspace = workspace or str(Path.cwd())
    
    # Create arbiter
    arbiter = ACPArbiter(
        workspace_root=workspace,
        objective=objective,
        strategy=strat,
        budget=budg,
        autonomy=AutonomyLevel.STANDARD
    )
    
    # Run
    run_dir = arbiter.run()
    
    # Collect summary
    summary = {
        "run_dir": str(run_dir),
        "run_id": arbiter.run_id,
        "agents_used": [config.name for config in arbiter.agent_configs],
        "models_used": [config.model for config in arbiter.agent_configs],
        "strategy": strategy,
        "budget": budget,
        "objective": objective,
        "status": "completed",  # TODO: determine actual status
        "checkpoints": len(arbiter.checkpoints),
        "arbiter_log": str(arbiter.log_file),
        "checkpoints_file": str(arbiter.checkpoints_file)
    }
    
    return summary


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: orchestrate.py <objective> [strategy] [budget]")
        sys.exit(1)
    
    objective = sys.argv[1]
    strategy = sys.argv[2] if len(sys.argv) > 2 else "auto"
    budget = sys.argv[3] if len(sys.argv) > 3 else "normal"
    
    summary = orchestrate(objective, strategy, budget)
    
    # Pretty print summary
    print("\n" + "="*60)
    print("ORCHESTRATION COMPLETE")
    print("="*60)
    print(f"Run ID: {summary['run_id']}")
    print(f"Strategy: {summary['strategy']}")
    print(f"Agents: {', '.join(summary['agents_used'])}")
    print(f"Models: {', '.join(summary['models_used'])}")
    print(f"Checkpoints: {summary['checkpoints']}")
    print(f"Status: {summary['status']}")
    print(f"\nResults: {summary['run_dir']}")
    print(f"Arbiter Log: {summary['arbiter_log']}")
    print("="*60 + "\n")
    
    # Also save as JSON
    summary_file = Path(summary['run_dir']) / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to: {summary_file}\n")


if __name__ == "__main__":
    main()
