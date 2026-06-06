"""Per-provider call implementations.

Isolates the SDK-specific code for each provider so that ModelManager can
dispatch to a single function regardless of which provider serves a given
task. Add a new provider here, then register it in
ModelManager._DISPATCH.

Each call_* function:
    - imports its SDK lazily (so optional providers don't break import)
    - reads required env vars via require_env()
    - wraps SDK errors in ProviderError
"""

from typing import Any

from .env_loader import require_env
from .exceptions import ProviderError


def call_lmstudio(model_id: str, prompt: str, **kwargs: Any) -> str:
    """Send a prompt to a local LM Studio server (OpenAI-compatible).

    Args:
        model_id: Model identifier loaded in LM Studio.
        prompt: User prompt text.
        **kwargs: Optional overrides - base_url, temperature, max_tokens.

    Returns:
        The model's response text.

    Raises:
        ProviderError: If the SDK is missing or the call fails.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ProviderError(
            "openai package required for LM Studio. "
            "Run: pip install openai"
        ) from exc

    base_url = kwargs.get("base_url", "http://localhost:1234/v1")
    client = OpenAI(base_url=base_url, api_key="lm-studio")
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1024),
        )
    except Exception as exc:
        raise ProviderError(f"LM Studio call failed: {exc}") from exc
    return response.choices[0].message.content or ""


def call_anthropic(model_id: str, prompt: str, **kwargs: Any) -> str:
    """Send a prompt to the Anthropic Claude API.

    Args:
        model_id: Anthropic model string (e.g. "claude-opus-4-7").
        prompt: User prompt text.
        **kwargs: Optional overrides - temperature, max_tokens.

    Returns:
        The model's response text.

    Raises:
        ProviderError: If the SDK is missing or the call fails.
    """
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise ProviderError(
            "anthropic package required. Run: pip install anthropic"
        ) from exc

    api_key = require_env("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=model_id,
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7),
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        raise ProviderError(f"Anthropic call failed: {exc}") from exc
    parts = [block.text for block in response.content if hasattr(block, "text")]
    return "".join(parts)


def call_google(model_id: str, prompt: str, **kwargs: Any) -> str:
    """Send a prompt to Google Gemini via the google-genai SDK.

    Reads GOOGLE_API_KEY from environment (matches Hub root .env convention).

    Args:
        model_id: Gemini model string (e.g. "gemini-2.5-flash").
        prompt: User prompt text.
        **kwargs: Optional overrides - temperature, max_output_tokens.

    Returns:
        The model's response text.

    Raises:
        ProviderError: If the SDK is missing or the call fails.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise ProviderError(
            "google-genai package required. Run: pip install google-genai"
        ) from exc

    api_key = require_env("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        temperature=kwargs.get("temperature", 0.7),
        max_output_tokens=kwargs.get("max_tokens", 1024),
    )
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config,
        )
    except Exception as exc:
        raise ProviderError(f"Gemini call failed: {exc}") from exc
    return response.text or ""
