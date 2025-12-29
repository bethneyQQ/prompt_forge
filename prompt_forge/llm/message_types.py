"""Unified message types for all LLM providers."""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ToolCall:
    """A tool call from the LLM."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Result of executing a tool."""
    tool_call_id: str
    content: str
    is_error: bool = False


@dataclass
class Message:
    """Unified message format for LLM conversations."""
    role: Literal["user", "assistant", "tool_result"]
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)

    @classmethod
    def user(cls, content: str) -> "Message":
        """Create a user message."""
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str, tool_calls: list[ToolCall] | None = None) -> "Message":
        """Create an assistant message."""
        return cls(role="assistant", content=content, tool_calls=tool_calls or [])

    @classmethod
    def tool_result(cls, results: list[ToolResult]) -> "Message":
        """Create a tool result message."""
        return cls(role="tool_result", tool_results=results)
