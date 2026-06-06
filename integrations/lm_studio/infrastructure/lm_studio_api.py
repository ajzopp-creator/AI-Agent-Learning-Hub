"""
LM Studio Native API Infrastructure
Low-level HTTP interactions with LM Studio's /api/v1/* endpoints.
No business logic — only fetch, send, and return raw data.

CHANGELOG
    2026-05-29 v1.2: Added post-load readiness wait in send_chat_request.
                     Fixes 400 Bad Request when chat fires before model is ready.
                     Added _wait_for_model_ready() helper.
    2026-05-30 v1.4: Fixed get_wrapper_status() JIT model detection bug.
                     Returns were inside the for-loop (evaluated only first
                     model entry). Added Pass 2 JIT fallback: if no
                     loaded_instances found, checks model list by ID so
                     JIT-configured LM Studio doesn't report false mismatch.
    2026-05-30 v1.6: Removed _suppress_to_diag() wraps and lms_suppress
                     import — console suppression did not work (LM Studio
                     server writes to the process console handle, not Python
                     stdout). Dead code removed.
"""

import asyncio
import httpx
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure Hub root is on path when run directly or imported from any project
_HUB_ROOT = Path(__file__).parent.parent.parent.parent
if str(_HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(_HUB_ROOT))
from integrations.lm_studio.config import (
    LM_STUDIO_CHAT_ENDPOINT,
    LM_STUDIO_MODELS_ENDPOINT,
    LM_STUDIO_LOAD_ENDPOINT,
    LM_STUDIO_UNLOAD_ENDPOINT,
    HTTP_TIMEOUT_SECONDS,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
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

# How long to wait between readiness polls after model load (seconds)
_MODEL_READY_POLL_INTERVAL = 2
# Max seconds to wait for model to be chat-ready after load returns True
_MODEL_READY_TIMEOUT = 20


async def _wait_for_model_ready(model_id: str) -> bool:
    """
    Poll until the given model_id appears in loaded_instances.

    LM Studio's load endpoint can return 200 before the model is fully
    initialized.  Sending a chat request in that window produces a 400.
    This helper polls the models list until the model shows as loaded
    or until _MODEL_READY_TIMEOUT seconds have elapsed.

    Args:
        model_id: The model ID string to wait for.

    Returns:
        True if model appears ready within timeout, False otherwise.
    """
    deadline = asyncio.get_event_loop().time() + _MODEL_READY_TIMEOUT
    while asyncio.get_event_loop().time() < deadline:
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
                response = await client.get(LM_STUDIO_MODELS_ENDPOINT)
                response.raise_for_status()
                data = response.json()
                for m in data.get("models", []):
                    for inst in m.get("loaded_instances", []):
                        if inst.get("id") == model_id:
                            return True
        except httpx.HTTPError:
            pass
        await asyncio.sleep(_MODEL_READY_POLL_INTERVAL)
    logger.warning(f"Model {model_id} not ready after {_MODEL_READY_TIMEOUT}s")
    return False


async def get_available_models() -> Optional[Dict[str, Any]]:
    """Fetch list of available models from LM Studio."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(LM_STUDIO_MODELS_ENDPOINT)
            response.raise_for_status()
            logger.info("Successfully fetched available models")
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch models: {e}")
        return None


async def load_model(model_id: str) -> bool:
    """
    Load a specific model in LM Studio.

    Retries up to MAX_RETRIES times on failure.  On success, waits for
    the model to appear in loaded_instances before returning True — this
    prevents the caller from sending a chat request before the model is
    actually ready (which causes a 400 Bad Request).
    """
    payload = {"model": model_id}

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
                response = await client.post(LM_STUDIO_LOAD_ENDPOINT, json=payload)
                response.raise_for_status()
                logger.info(f"Model loaded: {model_id}")
                # Wait for model to be chat-ready before returning
                await _wait_for_model_ready(model_id)
                return True
        except httpx.HTTPError as e:
            logger.warning(f"Load attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error(f"Failed to load model {model_id} after {MAX_RETRIES} attempts")
                return False
    return False


async def unload_model(model_id: Optional[str] = None) -> bool:
    """Unload a loaded model by instance_id."""
    payload = {"instance_id": model_id} if model_id else {}
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.post(
                LM_STUDIO_UNLOAD_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info(f"Model unloaded: {model_id or 'all'}")
            return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to unload model: {e}")
        return False


async def send_chat_request(
    messages: list[Dict[str, str]],
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Send a chat request to LM Studio native API.

    Endpoint: /api/v1/chat  (LM Studio native — NOT OpenAI-compatible)
    Payload uses 'input' field (not 'messages').

    Before sending, confirms the model appears in loaded_instances.
    This prevents 400 Bad Request errors when the model has just been loaded
    but is not yet fully initialized.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        model: Model ID (e.g., "deepseek-r1-distill-qwen-14b").
        temperature: Generation temperature (0.0 to 2.0).
        max_tokens: Maximum tokens to generate (None = model default).

    Returns:
        Response dict with model output or None if failed.
    """
    # Confirm model is ready before sending — prevents 400 on fresh loads
    is_ready = await _wait_for_model_ready(model)
    if not is_ready:
        logger.error(
            f"Aborting chat request: model {model} did not appear ready "
            f"within {_MODEL_READY_TIMEOUT}s"
        )
        return None

    # Convert messages array to single input string (native API format)
    input_text = "".join(msg.get("content", "") for msg in messages)

    payload: Dict[str, Any] = {
        "model": model,
        "input": input_text,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    logger.info(f"Sending chat request to {model}: input_len={len(input_text)}")
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS * 3) as client:
            response = await client.post(LM_STUDIO_CHAT_ENDPOINT, json=payload)
            response.raise_for_status()
            logger.info(f"Chat request successful: {model} (temp={temperature})")
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Chat request failed: {e}")
        return None


async def check_lm_studio_health() -> bool:
    """Quick health check — verify LM Studio is running and responsive."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(LM_STUDIO_MODELS_ENDPOINT)
            is_healthy = response.status_code == 200
            status = "healthy" if is_healthy else f"unhealthy (status {response.status_code})"
            logger.info(f"LM Studio health check: {status}")
            return is_healthy
    except httpx.HTTPError:
        logger.error("LM Studio is not responding — check if it's running")
        return False


def extract_message_from_response(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract the message content from LM Studio native API response.

    Response format:
        {"output": [{"type": "reasoning", "content": "..."}, {"type": "message", "content": "..."}]}

    Returns the first 'message'-type content block, or the first block as
    a fallback.  Returns None if response is empty or malformed.
    """
    if not response or "output" not in response:
        return None

    output_array = response.get("output", [])

    for item in output_array:
        if item.get("type") == "message":
            return item.get("content")

    if output_array:
        return output_array[0].get("content")

    return None


async def get_wrapper_status(task_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Query current LM Studio wrapper status without making changes.

    Read-only — no side effects, no LMS state changes.

    Args:
        task_type: Optional task type string (e.g. 'market_analysis').
                   If provided, expected_model is resolved from TASK_ROUTING.
                   If None, defaults to primary model.

    Returns dict with keys:
        lm_studio_running  bool      — Is LMS responding?
        current_model      str|None  — What model is loaded now?
        expected_model     str       — What we want for this task_type
        model_mismatch     bool      — Is wrong/no model loaded?
        action_required    str|None  — Human instruction if mismatch
        message            str       — Status summary
    """
    from integrations.lm_studio.config import MODELS, TASK_ROUTING

    if task_type and task_type in TASK_ROUTING:
        tier = TASK_ROUTING[task_type]
        expected_model = MODELS[tier]["id"]
    else:
        expected_model = MODELS["primary"]["id"]

    is_running = await check_lm_studio_health()

    if not is_running:
        return {
            "lm_studio_running": False,
            "current_model": None,
            "expected_model": expected_model,
            "model_mismatch": True,
            "action_required": (
                "LM Studio is not running. "
                "Launch: C:\\Program Files\\LM Studio\\LM Studio.exe"
            ),
            "message": "LM Studio not responding",
        }

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(LM_STUDIO_MODELS_ENDPOINT)
            response.raise_for_status()
            models_data = response.json()

        # Pass 1: check for an explicitly loaded instance.
        current_model = None
        for m in models_data.get("models", []):
            if m.get("loaded_instances"):
                current_model = m["loaded_instances"][0]["id"]
                break

        # Pass 2: JIT fallback — LM Studio may not pin models in
        # loaded_instances between calls ("just-in-time loading").
        # If the expected model exists anywhere in the model list,
        # treat it as available rather than reporting a false mismatch.
        jit_active = False
        if current_model is None:
            available_ids = [
                m.get("id", "") for m in models_data.get("models", [])
            ]
            if expected_model in available_ids:
                current_model = expected_model
                jit_active = True
                logger.info(
                    f"JIT model detected: {expected_model} present in "
                    f"model list but not pinned in loaded_instances"
                )

        if current_model == expected_model:
            jit_note = " (JIT — will load on first request)" if jit_active else ""
            return {
                "lm_studio_running": True,
                "current_model": current_model,
                "expected_model": expected_model,
                "model_mismatch": False,
                "action_required": None,
                "message": f"Ready — {current_model} is loaded and operational{jit_note}",
            }
        elif current_model:
            return {
                "lm_studio_running": True,
                "current_model": current_model,
                "expected_model": expected_model,
                "model_mismatch": True,
                "action_required": (
                    f"Wrong model loaded. Load: {expected_model} "
                    f"(currently: {current_model})"
                ),
                "message": f"Model mismatch: {current_model}",
            }
        else:
            return {
                "lm_studio_running": True,
                "current_model": None,
                "expected_model": expected_model,
                "model_mismatch": True,
                "action_required": f"No model loaded. Load: {expected_model}",
                "message": "LM Studio running but no model loaded",
            }
    except httpx.HTTPError as e:
        logger.error(f"Failed to query model status: {e}")
        return {
            "lm_studio_running": False,
            "current_model": None,
            "expected_model": expected_model,
            "model_mismatch": True,
            "action_required": "Error querying status — LM Studio may be starting up",
            "message": f"Query failed: {str(e)}",
        }
