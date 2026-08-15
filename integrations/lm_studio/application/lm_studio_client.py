"""
LM Studio Client — Main Orchestration Layer
Coordinates model loading/unloading, task routing, and chat execution.
Users interact with this client for all LM Studio operations.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from integrations.lm_studio.infrastructure.lm_studio_api import (
    load_model,
    unload_model,
    send_chat_request,
    check_lm_studio_health,
    get_available_models,
    extract_message_from_response,
)
from integrations.lm_studio.domain.task_router import (
    route_task,
    get_temperature_for_task,
    get_context_for_model,
)
from integrations.lm_studio.config import LOG_FILE

# ── LOGGING SETUP ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LMStudioClient:
    """
    Main interface for interacting with LM Studio.

    Handles:
    - Health checks against a running LM Studio instance
    - Model loading/unloading
    - Task-to-model routing
    - Chat request execution with appropriate parameters

    Does not auto-launch LM Studio -- that is the launcher's job
    (integrations.lm_studio.infrastructure.lm_studio_launcher), invoked
    explicitly by the operator or a project's startup flow, never
    implicitly from inside this orchestration layer.
    """

    def __init__(self):
        """Initialize the client with default state."""
        self.current_model: Optional[str] = None
        self.is_healthy = False

    async def startup(self) -> bool:
        """
        Initialize client — verify LM Studio is running and responsive.

        Returns:
            True if healthy, False otherwise.
        """
        logger.info("Starting LM Studio client initialization...")

        self.is_healthy = await check_lm_studio_health()
        if self.is_healthy:
            logger.info("LM Studio client initialized successfully")
        else:
            logger.error("LM Studio health check failed — launch LM Studio and retry")

        return self.is_healthy

    async def switch_model(self, model_id: Optional[str]) -> bool:
        """
        Unload current model (if any) and load a new one.

        Args:
            model_id: Model identifier to load, or None to unload only.

        Returns:
            True if successful, False otherwise.
        """
        if model_id is None:
            # Unload only
            if self.current_model:
                await unload_model()
                self.current_model = None
                logger.info("Model unloaded")
            return True

        if self.current_model == model_id:
            logger.info(f"Model {model_id} already loaded — skipping switch")
            return True

        # Unload current if one is loaded
        if self.current_model:
            logger.info(f"Unloading current model: {self.current_model}")
            await unload_model()

        # Load new model
        success = await load_model(model_id)
        if success:
            self.current_model = model_id
            logger.info(f"Switched to model: {model_id}")
        return success

    async def chat(
        self,
        messages: list[Dict[str, str]],
        task_type: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """
        Send a chat request to the currently loaded model.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            task_type: Optional task type for auto-routing. If provided, client
                       will load the appropriate model automatically.
            temperature: Optional override for generation temperature.
            max_tokens: Optional max tokens to generate.

        Returns:
            Response text (string) or None if failed.
        """
        if not self.is_healthy:
            logger.error("Client not healthy — run startup() first")
            return None

        # Auto-route if task_type provided
        if task_type:
            try:
                model_tier, model_id = route_task(task_type)
                success = await self.switch_model(model_id)
                if not success:
                    logger.error(f"Failed to load model for task: {task_type}")
                    return None
            except ValueError as e:
                logger.error(f"Task routing failed: {e}")
                return None

        if not self.current_model:
            logger.error("No model loaded — call switch_model() first")
            return None

        # Use provided temperature or infer from task
        if temperature is None and task_type:
            temperature = get_temperature_for_task(task_type)
        elif temperature is None:
            temperature = 0.7  # Default

        logger.info(f"Sending chat request to {self.current_model}")

        # Get raw response from API
        response = await send_chat_request(messages, self.current_model, temperature, max_tokens)

        if not response:
            logger.error("Chat request returned no response")
            return None

        # Extract message text from response
        message_text = extract_message_from_response(response)
        if not message_text:
            logger.warning("Response had no message content")
            return None

        logger.info(f"Chat response received ({len(message_text)} chars)")
        return message_text

    async def get_models(self) -> Optional[Dict[str, Any]]:
        """
        Fetch list of available models.

        Returns:
            Models dict or None if failed.
        """
        return await get_available_models()


# ── CONVENIENCE ASYNC RUNNER ──────────────────────────────────────────────────
def run_async(coro):
    """
    Helper to run async code from sync context.

    Args:
        coro: Coroutine to execute.

    Returns:
        Result from coroutine.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)
