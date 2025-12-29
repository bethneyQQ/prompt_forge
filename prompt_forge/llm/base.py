"""Abstract base classes for LLM clients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .message_types import Message, ToolCall
from .tool_types import ToolDefinition


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


@dataclass
class LLMResponse:
    """Unified response from LLM."""
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = ""
    usage: Optional[dict] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 16384,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        system: Optional[str] = None,
        tools: Optional[list[ToolDefinition]] = None,
    ) -> LLMResponse:
        """Send a chat completion request.

        Args:
            messages: Conversation history
            system: System prompt
            tools: Available tools for the LLM to call

        Returns:
            LLMResponse with content and any tool calls
        """
        pass

    @property
    @abstractmethod
    def provider(self) -> LLMProvider:
        """Return the provider type."""
        pass
