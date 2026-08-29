"""Domain logic for tool registration, schema extraction, and argument validation."""

import inspect
from typing import Any, Callable, Dict, List, get_type_hints
from pydantic import TypeAdapter, ValidationError

from schemas import ToolDefinition, ToolFunctionSchema


class ToolRegistry:
    """Registry maintaining tool functions and validated parameter adapters."""

    def __init__(self) -> None:
        """Initialize empty registry mappings."""
        self._tools: Dict[str, Callable[..., Any]] = {}
        self._schemas: List[Dict[str, Any]] = []
        self._adapters: Dict[str, Dict[str, TypeAdapter[Any]]] = {}

    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Register a Python function as an LLM-invokable tool.

        Args:
            func: Target callable to register.

        Returns:
            The original callable unmodified.
        """
        name = func.__name__
        doc = inspect.getdoc(func) or "No description provided."
        type_hints = get_type_hints(func)
        sig = inspect.signature(func)

        properties: Dict[str, Any] = {}
        required: List[str] = []
        param_adapters: Dict[str, TypeAdapter[Any]] = {}

        type_mapping = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        for param_name, param in sig.parameters.items():
            if param_name == "return":
                continue

            param_type = type_hints.get(param_name, Any)
            json_type = type_mapping.get(param_type, "string")
            param_adapters[param_name] = TypeAdapter(param_type)

            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter: {param_name}",
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        tool_def = ToolDefinition(
            function=ToolFunctionSchema(
                name=name,
                description=doc,
                parameters={
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            )
        )

        self._tools[name] = func
        self._schemas.append(tool_def.model_dump())
        self._adapters[name] = param_adapters
        return func

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Retrieve all OpenAI-compatible tool schemas.

        Returns:
            List of dictionary schemas for API payloads.
        """
        return self._schemas

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a registered tool function with Pydantic type validation.

        Args:
            tool_name: Function identifier.
            arguments: Dictionary of keyword arguments.

        Returns:
            Result value from the target function.

        Raises:
            ValueError: If tool is not found or parameter validation fails.
        """
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' is not registered.")

        adapters = self._adapters.get(tool_name, {})
        validated_args: Dict[str, Any] = {}

        for param, value in arguments.items():
            if param in adapters:
                try:
                    validated_args[param] = adapters[param].validate_python(value)
                except ValidationError as err:
                    raise ValueError(
                        f"Validation failed for parameter '{param}': {err.errors()[0]['msg']}"
                    ) from err
            else:
                validated_args[param] = value

        return self._tools[tool_name](**validated_args)


default_registry = ToolRegistry()
register_tool = default_registry.register