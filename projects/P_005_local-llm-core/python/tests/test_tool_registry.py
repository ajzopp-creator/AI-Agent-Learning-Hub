"""Regression tests for domain/tool_registry schema building and validation."""

import pytest
from domain.tool_registry import ToolRegistry


def test_registry_extracts_correct_schema() -> None:
    """Ensure register decorator extracts typed OpenAI parameters."""
    registry = ToolRegistry()

    @registry.register
    def sample_func(item_id: int, label: str = "default") -> str:
        """Sample function description."""
        return f"{item_id}:{label}"

    schemas = registry.get_schemas()
    assert len(schemas) == 1
    fn_schema = schemas[0]["function"]
    assert fn_schema["name"] == "sample_func"
    assert fn_schema["parameters"]["properties"]["item_id"]["type"] == "integer"
    assert fn_schema["parameters"]["properties"]["label"]["type"] == "string"
    assert "item_id" in fn_schema["parameters"]["required"]
    assert "label" not in fn_schema["parameters"]["required"]


def test_registry_pydantic_argument_validation() -> None:
    """Ensure registered tools validate and coerce types or raise ValueError."""
    registry = ToolRegistry()

    @registry.register
    def multiply(val: float, multiplier: int) -> float:
        """Multiply float by integer multiplier."""
        return val * multiplier

    # Valid coerced types
    res = registry.execute("multiply", {"val": "12.5", "multiplier": "3"})
    assert res == 37.5

    # Invalid type triggers ValueError
    with pytest.raises(ValueError, match="Validation failed for parameter"):
        registry.execute("multiply", {"val": "not-a-number", "multiplier": 3})


def test_registry_unregistered_tool_error() -> None:
    """Ensure executing an unlisted tool name raises a descriptive ValueError."""
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="is not registered"):
        registry.execute("non_existent_tool", {})