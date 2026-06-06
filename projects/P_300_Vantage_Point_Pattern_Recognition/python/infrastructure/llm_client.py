"""
FILE: llm_client.py
VERSION: 1.0
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Generic HTTP client for LM Studio's OpenAI-compatible chat completions
    endpoint. Used by the Stage 8 Post-Decision Narrator path; does NOT
    know about SignalReport or any narrator-specific structure.

    Caller supplies system + user prompts as plain strings; this module:
      1. POSTs to <base_url>/chat/completions with the messages array
      2. Catches every failure mode (connection refused, timeout, HTTP
         error, malformed JSON, missing fields) and returns None
      3. Strips DeepSeek R1 <think>...</think> reasoning blocks from the
         response content before returning the narration text
      4. Returns None if the response is empty after stripping (model
         emitted only reasoning) or if the <think> block was truncated
         by max_tokens (open tag with no closing tag)
      5. Logs all failures via logging.warning; never raises

    NFR-1 conformance: the calling code (daily_evaluate_pipeline) will set
    report.narration = call_lm_studio(...). A None return leaves narration
    as None; the BUY/WATCH/PASS classification is computed BEFORE this
    call and never depends on the return value. Same SPY input ALWAYS
    produces the same signal regardless of LM Studio state.

    Logging routed to stdout per M-011 so PowerShell doesn't render
    INFO/WARNING lines as red NativeCommandError noise.

CHANGELOG:
    - 2026-05-19 v1.0: Initial Stage 8 release.
    - 2026-05-30 v1.1: Removed _suppress_to_diag import and wrap —
                       suppression did not work (LM Studio server writes
                       to process console handle, not Python stdout).
                       Dead code removed.
"""
from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import requests

from config import (
    LM_STUDIO_BASE_URL,
    LM_STUDIO_MAX_TOKENS,
    LM_STUDIO_MODEL,
    LM_STUDIO_TEMPERATURE,
    LM_STUDIO_TIMEOUT_SECONDS,
    LOG_FORMAT,
    LOG_LEVEL,
)


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING — stdout per M-011 (avoids PowerShell NativeCommandError red)
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# THINK-TAG STRIPPING (DeepSeek R1 reasoning chain)
# ─────────────────────────────────────────────────────────────────────────────

# DeepSeek R1 emits reasoning between <think>...</think> tags before the
# final answer. Strip these server-side here before returning narration to
# the caller. Non-greedy DOTALL match handles single or multiple blocks.
_THINK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think_tags(text: str) -> str | None:
    """
    Strip <think>...</think> blocks from text.

    Returns:
        - cleaned text when at least one closed think block exists AND
          non-think content remains
        - cleaned text when no think tags present (plain answer)
        - None when think tag opened but never closed (max_tokens cut
          generation mid-reasoning)
        - None when cleaned text is empty (model emitted only reasoning,
          no final answer)
    """
    has_open = "<think>" in text
    has_close = "</think>" in text

    if has_open and not has_close:
        logger.warning(
            "LM Studio response contains unclosed <think> tag — likely "
            "max_tokens truncation. Treating as no-answer."
        )
        return None

    cleaned = _THINK_PATTERN.sub("", text).strip()
    if not cleaned:
        logger.warning(
            "LM Studio response empty after <think> strip — model emitted "
            "only reasoning, no final answer."
        )
        return None
    return cleaned


# ─────────────────────────────────────────────────────────────────────────────
# CHAT COMPLETIONS CALL
# ─────────────────────────────────────────────────────────────────────────────

def call_lm_studio(
    system_prompt: str,
    user_prompt: str,
    *,
    base_url: str = LM_STUDIO_BASE_URL,
    model: str = LM_STUDIO_MODEL,
    timeout_seconds: int = LM_STUDIO_TIMEOUT_SECONDS,
    max_tokens: int = LM_STUDIO_MAX_TOKENS,
    temperature: float = LM_STUDIO_TEMPERATURE,
) -> str | None:
    """
    POST a chat completion request to LM Studio.

    Returns the cleaned narration text on success; returns None on any
    failure mode:
      - LM Studio not running (ConnectionError)
      - Timeout (request exceeded timeout_seconds)
      - HTTP error (404 model not found, 500 internal, etc.)
      - Malformed JSON response
      - Missing/empty content field in response
      - Reasoning-only response (no final answer after <think> strip)
      - Truncated <think> block (max_tokens fired mid-reasoning)

    Never raises. All failures logged via logger.warning.

    Keyword-only overrides allow callers (and tests) to pass non-default
    values without keyword-shadowing the positional prompt arguments.
    """
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    logger.info(
        f"LM Studio call: model={model} temp={temperature} "
        f"max_tokens={max_tokens} timeout={timeout_seconds}s"
    )

    try:
        response = requests.post(url, json=payload, timeout=timeout_seconds)
    except requests.exceptions.ConnectionError as exc:
        logger.warning(
            f"LM Studio connection refused at {url}. Is LM Studio open "
            f"with the model loaded? Error: {exc}"
        )
        return None
    except requests.exceptions.Timeout:
        logger.warning(
            f"LM Studio call exceeded {timeout_seconds}s timeout."
        )
        return None
    except requests.exceptions.RequestException as exc:
        logger.warning(f"LM Studio request failed: {exc}")
        return None

    if response.status_code != 200:
        logger.warning(
            f"LM Studio HTTP {response.status_code}: {response.text[:300]}"
        )
        return None

    try:
        data = response.json()
    except ValueError as exc:
        logger.warning(f"LM Studio response not valid JSON: {exc}")
        return None

    try:
        raw_content: str = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        keys_info = (
            list(data.keys()) if isinstance(data, dict) else type(data).__name__
        )
        logger.warning(
            f"LM Studio response missing expected fields "
            f"(choices[0].message.content): {exc}. Response shape: {keys_info}"
        )
        return None

    if not isinstance(raw_content, str) or not raw_content.strip():
        logger.warning("LM Studio response content empty or non-string.")
        return None

    cleaned = _strip_think_tags(raw_content)
    if cleaned is None:
        return None

    logger.info(
        f"LM Studio narration generated: {len(cleaned)} chars "
        f"({len(raw_content)} raw before think-strip)"
    )
    return cleaned
