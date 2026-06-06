"""LM Studio API caller for KB email summarization.

Calls LM Studio at http://127.0.0.1:1234/v1 with retry + fallback to
plain-text when LM Studio is unreachable or times out.
"""

import requests
import re
import logging
from typing import Optional

logger = logging.getLogger("p805")


def summarize(
    text: str,
    url: str = "http://127.0.0.1:1234/v1",
    model: str = "mistral",
    temperature: float = 0.3,
    max_tokens: int = 300,
    timeout: int = 10,
) -> Optional[str]:
    """Summarize email text via LM Studio. Return summary on success, None on failure.

    Args:
        text: Email body to summarize
        url: LM Studio API base URL
        model: Model name (default: mistral)
        temperature: Sampling temperature (default: 0.3)
        max_tokens: Max tokens in response (default: 300)
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Summarized text on success, None on failure (caller should fall back to full text)
    """
    if not text or len(text.strip()) < 10:
        logger.debug("Text too short to summarize; returning None")
        return None

    system_prompt = (
        "You are a financial research assistant. Summarize this email in 2-3 sentences. "
        "Focus: thesis, data points, action insights. Omit: greetings, signatures, marketing."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(f"{url}/chat/completions", json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            summary = data["choices"][0]["message"]["content"].strip()
            # Strip <think>...</think> blocks from reasoning models (e.g. deepseek-r1)
            summary = re.sub(r"<think>.*?</think>\s*", "", summary, flags=re.DOTALL).strip()
            logger.debug(f"LM Studio summarization succeeded ({len(summary)} chars)")
            return summary
        else:
            logger.warning("LM Studio response missing choices field")
            return None

    except requests.exceptions.Timeout:
        logger.warning(f"LM Studio timeout after {timeout}s; falling back to full text")
        return None
    except requests.exceptions.ConnectionError:
        logger.warning("LM Studio unreachable (connection refused); falling back to full text")
        return None
    except requests.exceptions.RequestException as e:
        body = ""
        if hasattr(e, "response") and e.response is not None:
            try:
                body = e.response.text[:500]
            except Exception:
                pass
        logger.warning(
            f"LM Studio request failed ({e}); response body: {body}; "
            f"falling back to full text"
        )
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling LM Studio: {e}")
        return None
