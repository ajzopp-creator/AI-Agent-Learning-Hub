"""
Task Routing Logic
Pure business logic to determine which model tier should handle a given task.
No I/O, no API calls — just decision-making.
"""

import logging
from typing import Tuple
from config import (
    TASK_ROUTING,
    MODELS,
    TEMPERATURE_SETTINGS,
    CONTEXT_LENGTH,
    LOG_FILE,
)

# ── LOGGING SETUP ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def route_task(task_type: str) -> Tuple[str, str]:
    """
    Determine which model tier should handle a task.
    
    Args:
        task_type: Task category (e.g., "market_analysis", "trade_journal_analysis")
    
    Returns:
        Tuple of (model_tier, model_id)
    
    Raises:
        ValueError: If task_type is not recognized.
    """
    if task_type not in TASK_ROUTING:
        available = ", ".join(sorted(TASK_ROUTING.keys()))
        raise ValueError(
            f"Unknown task type: {task_type}\n"
            f"Available: {available}"
        )
    
    model_tier = TASK_ROUTING[task_type]
    model_config = MODELS[model_tier]
    
    logger.info(f"Task '{task_type}' routed to {model_tier} ({model_config['id']})")
    return model_tier, model_config["id"]


def get_temperature_for_task(task_type: str) -> float:
    """
    Get the appropriate temperature setting for a task.
    
    Args:
        task_type: Task category.
    
    Returns:
        Temperature value (0.0 to 2.0).
    """
    # Categorize task into one of three temperature profiles
    if "coding" in task_type or "code" in task_type or "schema" in task_type:
        return TEMPERATURE_SETTINGS["coding"]  # 0.3 — deterministic
    elif "creative" in task_type or "generate" in task_type:
        return TEMPERATURE_SETTINGS["creative"]  # 0.9 — exploratory
    else:
        return TEMPERATURE_SETTINGS["analysis"]  # 0.7 — balanced


def get_context_for_model(model_tier: str) -> int:
    """
    Get the context window size for a model tier.
    
    Args:
        model_tier: One of "primary", "batch", "long_context"
    
    Returns:
        Context length in tokens.
    """
    return CONTEXT_LENGTH.get(model_tier, 8192)


def get_model_info(model_tier: str) -> dict:
    """
    Get full model configuration for a tier.
    
    Args:
        model_tier: One of "primary", "batch", "long_context"
    
    Returns:
        Dict with model_id, name, vram_gb, use_case, context_length, temperature.
    """
    config = MODELS[model_tier]
    return {
        "model_id": config["id"],
        "name": config["name"],
        "vram_gb": config["vram_gb"],
        "use_case": config["use_case"],
        "context_length": get_context_for_model(model_tier),
        "temperature": get_temperature_for_task(model_tier),
    }


def validate_task_type(task_type: str) -> bool:
    """
    Check if a task type is recognized.
    
    Args:
        task_type: Task category.
    
    Returns:
        True if valid, False otherwise.
    """
    return task_type in TASK_ROUTING


def list_all_tasks() -> list[str]:
    """
    List all recognized task types.
    
    Returns:
        Sorted list of task type strings.
    """
    return sorted(TASK_ROUTING.keys())
