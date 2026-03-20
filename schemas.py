from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AnthropicTool(BaseModel):
    name: str
    description: str | None = None
    input_schema: dict[str, Any] = Field(default_factory=dict)


class AnthropicMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str | list[dict[str, Any]]


class AnthropicRequest(BaseModel):
    model: str = "claude-sonnet-4-20250514"
    messages: list[AnthropicMessage] = Field(default_factory=list)
    max_tokens: int = 4096
    stream: bool = False
    system: str | list[dict[str, Any]] | None = None
    tools: list[AnthropicTool] = Field(default_factory=list)
    tool_choice: dict[str, Any] | None = None
    temperature: float | None = None
    top_p: float | None = None
    stop_sequences: list[str] | None = None
    thinking: dict[str, Any] | None = None


class CountTokensResponse(BaseModel):
    input_tokens: int
