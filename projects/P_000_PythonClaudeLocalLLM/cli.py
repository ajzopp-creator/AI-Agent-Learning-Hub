"""
LM Studio Wrapper — Command-Line Interface (CLI)
Provides operator-facing commands for health checks, model info, and task routing.
Primary entry point for automation and manual verification.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

# Add Hub root to path for canonical wrapper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integrations.lm_studio.application.lm_studio_client import LMStudioClient
from integrations.lm_studio.domain.task_router import (
    list_all_tasks,
    validate_task_type,
    get_model_info,
    route_task,
)
from integrations.lm_studio.config import MODELS, TASK_ROUTING, LM_STUDIO_API_BASE


async def health_check():
    """Run full health check: LM Studio, models, task routing."""
    print("\n" + "="*70)
    print("LM STUDIO WRAPPER — HEALTH CHECK")
    print("="*70 + "\n")
    
    client = LMStudioClient()
    is_healthy = await client.startup()
    
    if not is_healthy:
        print("✗ LM Studio health check FAILED")
        print("  Run: python test_health_check.py (auto-starts LM Studio)")
        return False
    
    print("✓ LM Studio is healthy")
    print(f"✓ API Endpoint: {LM_STUDIO_API_BASE}")
    
    models = await client.get_models()
    if models:
        model_list = models.get("data", [])
        print(f"✓ {len(model_list)} model(s) available in LM Studio")
    
    print(f"✓ {len(TASK_ROUTING)} task types configured")
    print("\n✓ WRAPPER HEALTHY\n")
    return True


async def model_info():
    """Display all three-tier models and their configurations."""
    print("\n" + "="*70)
    print("MODEL STACK CONFIGURATION")
    print("="*70 + "\n")
    
    for tier in ["primary", "batch", "long_context"]:
        info = get_model_info(tier)
        print(f"Tier: {tier.upper()}")
        print(f"  Model ID:        {info['model_id']}")
        print(f"  Name:            {info['name']}")
        print(f"  Context Length:  {info['context_length']} tokens")
        print(f"  Use Case:        {MODELS[tier]['use_case']}")
        print()


def task_routing():
    """Display task-to-model routing table."""
    print("\n" + "="*70)
    print("TASK ROUTING TABLE")
    print("="*70 + "\n")
    
    # Group by model tier
    routing_by_tier = {}
    for task, tier in TASK_ROUTING.items():
        if tier not in routing_by_tier:
            routing_by_tier[tier] = []
        routing_by_tier[tier].append(task)
    
    for tier in ["primary", "batch", "long_context"]:
        if tier in routing_by_tier:
            print(f"{tier.upper()} ({MODELS[tier]['id']}):")
            for task in sorted(routing_by_tier[tier]):
                print(f"  • {task}")
            print()


async def route_example(task_type: str):
    """Show which model handles a specific task type."""
    if not validate_task_type(task_type):
        print(f"\n✗ Unknown task type: {task_type}")
        print("\nAvailable task types:")
        for task in list_all_tasks():
            print(f"  • {task}")
        return False
    
    tier, model_id = route_task(task_type)
    info = get_model_info(tier)
    
    print(f"\nTask: {task_type}")
    print(f"Routes to: {tier.upper()}")
    print(f"Model: {info['model_id']}")
    print(f"Context: {info['context_length']} tokens")
    print(f"Use Case: {MODELS[tier]['use_case']}")
    return True


def catalog_summary():
    """
    Placeholder for catalog integration (future: P_300 pattern).
    Currently displays wrapper metadata.
    """
    print("\n" + "="*70)
    print("WRAPPER METADATA")
    print("="*70 + "\n")
    
    metadata = {
        "wrapper_version": "1.0",
        "created": "2026-05-28",
        "models": {
            "primary": MODELS["primary"]["id"],
            "batch": MODELS["batch"]["id"],
            "long_context": MODELS["long_context"]["id"],
        },
        "task_types_count": len(TASK_ROUTING),
        "api_endpoint": LM_STUDIO_API_BASE,
        "python_interpreter": str(Path(sys.executable)),
    }
    
    print(json.dumps(metadata, indent=2))


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("""
LM Studio Wrapper — Command-Line Interface

Usage:
  python cli.py health-check        Run full health check
  python cli.py model-info          Show all three-tier models
  python cli.py task-routing        Display task-to-model routing table
  python cli.py route <task_type>   Show which model handles a task
  python cli.py catalog-summary     Display wrapper metadata
  python cli.py help                Show this help message

Examples:
  python cli.py health-check
  python cli.py route market_analysis
  python cli.py route trade_journal_analysis
        """)
        return 0
    
    command = sys.argv[1].lower()
    
    if command == "help":
        main()
        return 0
    
    elif command == "health-check":
        result = asyncio.run(health_check())
        return 0 if result else 1
    
    elif command == "model-info":
        asyncio.run(model_info())
        return 0
    
    elif command == "task-routing":
        task_routing()
        return 0
    
    elif command == "route":
        if len(sys.argv) < 3:
            print("Usage: python cli.py route <task_type>")
            return 1
        task_type = sys.argv[2]
        result = asyncio.run(route_example(task_type))
        return 0 if result else 1
    
    elif command == "catalog-summary":
        catalog_summary()
        return 0
    
    else:
        print(f"Unknown command: {command}")
        print("Run: python cli.py help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
