"""Application orchestrator coordinating the multi-turn tool calling agent loop."""

import json
import logging
from typing import Any, Dict, List, Optional

import config
from domain.tool_registry import ToolRegistry, default_registry
from infrastructure.lms_client import LMStudioClient
from schemas import ToolExecutionResult

# Import shell_runner to ensure default tools register
import infrastructure.shell_runner  # noqa: F401

logger = logging.getLogger(__name__)


class ToolOrchestrator:
    """Orchestrates tool dispatch, execution, and response synthesis."""

    def __init__(
        self,
        client: Optional[LMStudioClient] = None,
        registry: Optional[ToolRegistry] = None,
    ) -> None:
        """Initialize orchestrator dependencies."""
        self.client = client or LMStudioClient()
        self.registry = registry or default_registry

    def run(
        self,
        prompt: str,
        max_iterations: int = config.MAX_TOOL_ITERATIONS,
        verbose: bool = True,
    ) -> str:
        """Execute the prompt-eval-execute loop until final synthesis is reached.

        Args:
            prompt: User input prompt.
            max_iterations: Maximum loop iterations.
            verbose: Whether to log step-by-step trace to console.

        Returns:
            Final synthesized response string.
        """
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": "You are an assistant with access to local tools. Use tools when required.",
            },
            {"role": "user", "content": prompt},
        ]

        tools = self.registry.get_schemas()
        model_name = self.client.app_cfg.model_defaults.model_alias

        for step in range(max_iterations):
            if verbose:
                logger.info("[Iteration %d] Requesting completion from %s...", step + 1, model_name)

            response = self.client.chat_completion(
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.0,
            )

            choice = response.choices[0]
            msg = choice.message

            if not msg.tool_calls:
                if verbose:
                    logger.info("[Completed] Final response generated.")
                return msg.content or ""

            if verbose:
                logger.info("[Tool Request] %d tool call(s) requested.", len(msg.tool_calls))

            tool_calls_payload = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": tool_calls_payload,
            })

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args_raw = tool_call.function.arguments

                try:
                    fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
                except json.JSONDecodeError:
                    fn_args = {}

                if verbose:
                    logger.info("  -> Invoking: %s(%s)", fn_name, fn_args)

                try:
                    result = self.registry.execute(fn_name, fn_args)
                    exec_result = ToolExecutionResult(status="success", result=result)
                except Exception as err:
                    logger.error("  <- Tool execution error in %s: %s", fn_name, err)
                    exec_result = ToolExecutionResult(status="error", error=str(err))

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": exec_result.model_dump_json(),
                })

        return "Tool loop exceeded maximum iterations without reaching a final response."