"""
LM Studio Native API Infrastructure
Low-level HTTP interactions with LM Studio's /api/v1/* endpoints.
No business logic — only fetch, send, and return raw data.
"""

import asyncio
import httpx
import logging
from typing import Any, Dict, Optional
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
    """Load a specific model in LM Studio."""
    payload = {"model": model_id}
    
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
                response = await client.post(LM_STUDIO_LOAD_ENDPOINT, json=payload)
                response.raise_for_status()
                logger.info(f"Model loaded: {model_id}")
                return True
        except httpx.HTTPError as e:
            logger.warning(f"Load attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error(f"Failed to load model {model_id} after {MAX_RETRIES} attempts")
                return False


async def unload_model() -> bool:
    """Unload the currently loaded model."""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.post(LM_STUDIO_UNLOAD_ENDPOINT)
            response.raise_for_status()
            logger.info("Model unloaded successfully")
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
    
    Native API format: /api/v1/chat uses 'input' field (not 'messages')
    Converts messages to single input string.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        model: Model ID (e.g., "deepseek-r1-distill-qwen-14b").
        temperature: Generation temperature (0.0 to 2.0).
        max_tokens: Maximum tokens to generate (None = model default).
    
    Returns:
        Response dict with model output or None if failed.
        Response format: {
            'model_instance_id': '...',
            'output': [{'type': 'reasoning'|'message', 'content': '...'}, ...],
            'stats': {...}
        }
    """
    # Convert messages array to single input string
    input_text = ""
    for msg in messages:
        content = msg.get("content", "")
        input_text += content
    
    payload = {
        "model": model,  # REQUIRED
        "input": input_text,  # REQUIRED by native API
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
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
    Extract the message content from LM Studio API response.
    
    Response format:
    {
        'output': [
            {'type': 'reasoning', 'content': '...'},
            {'type': 'message', 'content': '...'}
        ]
    }
    
    Args:
        response: Response dict from LM Studio API
    
    Returns:
        Message text or None if not found
    """
    if not response or 'output' not in response:
        return None
    
    output_array = response.get('output', [])
    
    # Look for 'message' type output (skip 'reasoning' type)
    for output_item in output_array:
        if output_item.get('type') == 'message':
            return output_item.get('content')
    
    # Fallback: return first output's content
    if output_array:
        return output_array[0].get('content')
    
    return None


async def get_wrapper_status(task_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Query current LM Studio wrapper status without making changes.

    Designed for projects to check state before deciding what to do.
    Read-only operation — no side effects, no changes to LMS state.

    Args:
        task_type: Optional task type string (e.g. 'market_analysis').
                   If provided, expected_model is resolved from TASK_ROUTING.
                   If None, defaults to primary model.

    Returns dict with keys:
        'lm_studio_running': bool              — Is LMS responding?
        'current_model': str or None           — What model is loaded now?
        'expected_model': str                  — What we want for this task_type
        'model_mismatch': bool                 — Is wrong/no model loaded?
        'action_required': str or None         — Human instruction if mismatch
        'message': str                         — Status summary
    """
    from integrations.lm_studio.config import MODELS, TASK_ROUTING

    # Resolve expected model from task_type, default to primary
    if task_type and task_type in TASK_ROUTING:
        tier = TASK_ROUTING[task_type]
        expected_model = MODELS[tier]["id"]
    else:
        expected_model = MODELS["primary"]["id"]
    
    # Check if LM Studio is responding at all
    is_running = await check_lm_studio_health()
    
    if not is_running:
        return {
            'lm_studio_running': False,
            'current_model': None,
            'expected_model': expected_model,
            'model_mismatch': True,
            'action_required': 'LM Studio is not running. Launch: C:\\Program Files\\LM Studio\\LM Studio.exe',
            'message': 'LM Studio not responding'
        }
    
    # Try to get the currently loaded model
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(LM_STUDIO_MODELS_ENDPOINT)
            response.raise_for_status()
            models_data = response.json()
            
            # Response: {"models": [{"key": "...", "loaded_instances": [{"id": "..."}], ...}]}
            # A model is loaded when its loaded_instances list is non-empty.
            current_model = None
            for m in models_data.get('models', []):
                if m.get('loaded_instances'):
                    current_model = m['loaded_instances'][0]['id']
                    break
            
            if current_model == expected_model:
                # Correct model is loaded ✓
                return {
                    'lm_studio_running': True,
                    'current_model': current_model,
                    'expected_model': expected_model,
                    'model_mismatch': False,
                    'action_required': None,
                    'message': f'Ready — {current_model} is loaded and operational'
                }
            elif current_model:
                # Wrong model is loaded
                return {
                    'lm_studio_running': True,
                    'current_model': current_model,
                    'expected_model': expected_model,
                    'model_mismatch': True,
                    'action_required': f'Wrong model loaded. Load: {expected_model} (currently: {current_model})',
                    'message': f'Model mismatch: {current_model}'
                }
            else:
                # No model is loaded
                return {
                    'lm_studio_running': True,
                    'current_model': None,
                    'expected_model': expected_model,
                    'model_mismatch': True,
                    'action_required': f'No model loaded. Load: {expected_model}',
                    'message': 'LM Studio running but no model loaded'
                }
    except httpx.HTTPError as e:
        logger.error(f"Failed to query model status: {e}")
        return {
            'lm_studio_running': False,
            'current_model': None,
            'expected_model': expected_model,
            'model_mismatch': True,
            'action_required': 'Error querying status — LM Studio may be starting up',
            'message': f'Query failed: {str(e)}'
        }
