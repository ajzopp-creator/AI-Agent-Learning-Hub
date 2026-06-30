"""LLM caller for KB email summarization and direction classification.

Primary: Gemini 2.0 Flash (via google-genai).
Fallback: LM Studio at http://127.0.0.1:1234/v1 (local, no API key needed).

All LLM config (URLs, models, timeouts) lives in config.py.
Application layer calls classify_direction(ticker, context) only —
no LLM params leak into the application layer.

Gemini API key loaded from python/.env — never hardcoded.
"""

import os
import re
import logging
import requests
from typing import Optional

import config

logger = logging.getLogger("p805")


# ---------------------------------------------------------------------------
# Key loading
# ---------------------------------------------------------------------------

def _load_gemini_key() -> Optional[str]:
    """Load GEMINI_API_KEY from .env file next to this package, then env vars."""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        load_dotenv(dotenv_path=os.path.abspath(env_path), override=False)
    except ImportError:
        pass
    return os.environ.get("GEMINI_API_KEY")


# ---------------------------------------------------------------------------
# LM Studio helpers
# ---------------------------------------------------------------------------

def _get_lm_model_id() -> str:
    """Return the loaded model ID from LM Studio, falling back to config default."""
    try:
        response = requests.get(f"{config.LM_STUDIO_URL}/models", timeout=5)
        response.raise_for_status()
        models = response.json().get("data", [])
        if models:
            return models[0]["id"]
    except Exception as e:
        logger.warning(f"Could not fetch LM Studio model ID: {e}")
    return config.LM_STUDIO_MODEL


def _lm_studio_chat(messages: list, max_tokens: int = 300, temperature: float = 0.0) -> Optional[str]:
    """Call LM Studio chat completions. Return content text or None on failure."""
    model = _get_lm_model_id()
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        response = requests.post(
            f"{config.LM_STUDIO_URL}/chat/completions",
            json=payload,
            timeout=config.LM_STUDIO_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        msg = data["choices"][0]["message"]
        raw = msg.get("content", "").strip() or msg.get("reasoning_content", "").strip()
        raw = re.sub(r"<think>.*?</think>\s*", "", raw, flags=re.DOTALL).strip()
        return raw or None
    except requests.exceptions.ConnectionError:
        logger.warning("LM Studio unreachable (connection refused)")
        return None
    except requests.exceptions.Timeout:
        logger.warning(f"LM Studio timeout after {config.LM_STUDIO_TIMEOUT}s")
        return None
    except requests.exceptions.RequestException as e:
        body = ""
        if hasattr(e, "response") and e.response is not None:
            try:
                body = e.response.text[:300]
            except Exception:
                pass
        logger.warning(f"LM Studio request error ({e}); body: {body}")
        return None
    except Exception as e:
        logger.error(f"Unexpected LM Studio error: {e}")
        return None


# ---------------------------------------------------------------------------
# Gemini helpers
# ---------------------------------------------------------------------------

def _gemini_generate(prompt: str, max_tokens: int = 300) -> Optional[str]:
    """Send a prompt to Gemini 2.0 Flash via google-genai SDK. Return text or None."""
    api_key = _load_gemini_key()
    if not api_key:
        logger.warning("GEMINI_API_KEY not set; skipping Gemini call")
        return None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.0,
            ),
        )
        return response.text.strip() if response.text else None
    except Exception as e:
        logger.warning(f"Gemini call failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API — application layer calls only these two functions
# ---------------------------------------------------------------------------

def classify_direction(ticker: str, context: str) -> str:
    """Classify direction for one ticker+context.

    Tries Gemini 2.0 Flash first; falls back to LM Studio if Gemini fails.
    Returns one of: 'long', 'short', 'watch', 'unknown'. Never raises.
    """
    valid = {"long", "short", "watch", "unknown"}
    synonyms = {"bullish": "long", "bearish": "short", "neutral": "watch", "unclear": "unknown"}

    if not context or len(context.strip()) < 5:
        return "unknown"

    prompt = (
        f"Ticker: {ticker}\n"
        f"Text: {context}\n\n"
        "Is the sentiment toward this ticker bullish (long), bearish (short), "
        "neutral/monitoring (watch), or unclear (unknown)?\n"
        "Reply with exactly one word: long, short, watch, or unknown."
    )

    def _parse(raw: Optional[str]) -> Optional[str]:
        if not raw:
            return None
        word = raw.lower().split()[0].rstrip(".,!?") if raw.lower().split() else ""
        word = synonyms.get(word, word)
        return word if word in valid else None

    result = _parse(_gemini_generate(prompt, max_tokens=10))
    if result:
        logger.debug(f"Gemini classified {ticker} → {result}")
        return result

    result = _parse(_lm_studio_chat(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    ))
    if result:
        logger.debug(f"LM Studio classified {ticker} → {result}")
        return result

    return "unknown"


def summarize(text: str, max_tokens: int = 300) -> Optional[str]:
    """Summarize email text. Tries Gemini first, falls back to LM Studio.

    Returns summary string on success, None on total failure.
    """
    if not text or len(text.strip()) < 10:
        logger.debug("Text too short to summarize; returning None")
        return None

    system = (
        "You are a financial research assistant. Summarize this email in 2-3 sentences. "
        "Focus: thesis, data points, action insights. Omit: greetings, signatures, marketing."
    )

    summary = _gemini_generate(f"{system}\n\n{text}", max_tokens=max_tokens)
    if summary:
        logger.debug(f"Gemini summarization succeeded ({len(summary)} chars)")
        return summary

    summary = _lm_studio_chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    if summary:
        logger.debug(f"LM Studio summarization succeeded ({len(summary)} chars)")
        return summary

    return None
