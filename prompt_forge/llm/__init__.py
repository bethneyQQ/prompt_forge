"""LLM abstraction layer supporting multiple providers."""

from typing import Optional

from .base import BaseLLMClient, LLMProvider, LLMResponse
from .anthropic_client import AnthropicClient
from .openrouter_client import OpenRouterClient
from .dashscope_client import DashScopeClient
from .message_types import Message, ToolCall, ToolResult
from .tool_types import ToolDefinition, ToolParameter


def create_llm_client(
    provider: LLMProvider | str,
    api_key: str,
    model: Optional[str] = None,
    **kwargs
) -> BaseLLMClient:
    """
    Factory function to create appropriate LLM client.

    Args:
        provider: "anthropic" or "openrouter"
        api_key: API key for the provider
        model: Model identifier (optional, uses defaults)
        **kwargs: Additional provider-specific options

    Returns:
        Configured LLM client instance
    """
    if isinstance(provider, str):
        provider = LLMProvider(provider.lower())

    if provider == LLMProvider.ANTHROPIC:
        return AnthropicClient(
            api_key=api_key,
            model=model or "claude-opus-4-5-20251101",
            **kwargs
        )
    elif provider == LLMProvider.OPENROUTER:
        return OpenRouterClient(
            api_key=api_key,
            model=model or "anthropic/claude-opus-4.5",
            **kwargs
        )
    elif provider == LLMProvider.DASHSCOPE:
        return DashScopeClient(
            api_key=api_key,
            model=model or "qwen-max",
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


__all__ = [
    # Base classes
    "BaseLLMClient",
    "LLMProvider",
    "LLMResponse",
    # Client implementations
    "AnthropicClient",
    "OpenRouterClient",
    "DashScopeClient",
    # Message types
    "Message",
    "ToolCall",
    "ToolResult",
    # Tool types
    "ToolDefinition",
    "ToolParameter",
    # Factory
    "create_llm_client",
]
