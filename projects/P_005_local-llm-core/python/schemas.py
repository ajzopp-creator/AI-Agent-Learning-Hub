"""Pydantic schemas for runtime configuration, tool definitions, and benchmarks."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server connection configuration."""

    base_url: str = Field(default="http://127.0.0.1:1234/v1")
    api_key: str = Field(default="lm-studio")
    timeout_seconds: float = Field(default=60.0)


class ModelDefaults(BaseModel):
    """Model default generation parameters."""

    model_alias: str = Field(default="granite-4.1-8b")
    temperature: float = Field(default=0.0)
    top_p: float = Field(default=0.95)
    max_tokens: int = Field(default=2048)
    stream: bool = Field(default=False)


class GuardrailConfig(BaseModel):
    """Token context limit configurations."""

    max_context_tokens: int = Field(default=8192)
    reserve_output_tokens: int = Field(default=1024)


class AppConfig(BaseModel):
    """Top-level application configuration schema."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    model_defaults: ModelDefaults = Field(default_factory=ModelDefaults)
    guardrails: GuardrailConfig = Field(default_factory=GuardrailConfig)


class ToolFunctionSchema(BaseModel):
    """OpenAI-compatible function schema definition."""

    name: str
    description: str
    parameters: Dict[str, Any]


class ToolDefinition(BaseModel):
    """OpenAI-compatible tool wrapper."""

    type: str = "function"
    function: ToolFunctionSchema


class ToolExecutionResult(BaseModel):
    """Result envelope for executed tool functions."""

    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


class BenchmarkMetrics(BaseModel):
    """Raw inference performance benchmark metrics."""

    ttft_ms: float
    total_duration_sec: float
    tokens_generated: int
    tokens_per_sec: float


class TestCaseResult(BaseModel):
    """Result record for tool evaluation test cases."""

    __test__ = False  # Prevent Pytest from collecting this schema as a test suite

    case_id: str
    passed: bool
    latency_sec: float
    output_preview: str