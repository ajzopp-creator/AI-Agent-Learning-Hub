"""Infrastructure client for communicating with LM Studio OpenAI-compatible endpoint."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from openai import OpenAI, APIConnectionError, APITimeoutError

import config
from schemas import AppConfig

logger = logging.getLogger(__name__)


class LMStudioClient:
    """OpenAI SDK wrapper for local LM Studio API interactions."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize the client using model configuration schema.

        Args:
            config_path: Optional custom path to model_config.json.
        """
        target_path = config_path or config.MODEL_CONFIG_PATH
        self.app_cfg = self._load_app_config(target_path)

        self.client = OpenAI(
            base_url=self.app_cfg.server.base_url,
            api_key=self.app_cfg.server.api_key,
            timeout=self.app_cfg.server.timeout_seconds,
        )

    def _load_app_config(self, path: Path) -> AppConfig:
        """Load and parse configuration with BOM-safe UTF-8 decoding.

        Args:
            path: Target JSON file path.

        Returns:
            Validated AppConfig Pydantic model.
        """
        if not path.exists():
            logger.warning("Config not found at %s. Using default schema.", path)
            return AppConfig()

        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                return AppConfig.model_validate(data)
        except Exception as e:
            logger.error("Failed to load config from %s: %s. Reverting to defaults.", path, e)
            return AppConfig()

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        stream: bool = False,
    ) -> Any:
        """Dispatch a chat completion request to LM Studio.

        Args:
            messages: List of chat messages.
            temperature: Generation temperature override.
            max_tokens: Output token limit override.
            tools: Optional tool schemas.
            tool_choice: Optional tool choice setting ('auto').
            stream: Whether to stream tokens.

        Returns:
            OpenAI chat completion response or stream iterator.

        Raises:
            ConnectionError: If server connection is refused.
            TimeoutError: If request times out.
        """
        params: Dict[str, Any] = {
            "model": self.app_cfg.model_defaults.model_alias,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.app_cfg.model_defaults.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.app_cfg.model_defaults.max_tokens,
            "stream": stream,
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice or "auto"

        try:
            return self.client.chat.completions.create(**params)
        except APIConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to LM Studio at {self.app_cfg.server.base_url}. Ensure server is running."
            ) from e
        except APITimeoutError as e:
            raise TimeoutError("LM Studio request timed out during inference.") from e

    def stream_response(self, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Yield generated token deltas from streaming completion.

        Args:
            messages: List of chat messages.

        Yields:
            Token string deltas as they arrive.
        """
        stream = self.chat_completion(messages=messages, stream=True)
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta