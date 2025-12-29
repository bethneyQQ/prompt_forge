"""Anthropic SDK client implementation."""

from typing import Optional

import anthropic

from .base import BaseLLMClient, LLMResponse, LLMProvider
from .message_types import Message, ToolCall
from .tool_types import ToolDefinition


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic's Claude API using native SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-4-5-20251101",
        temperature: float = 0.3,
        max_tokens: int = 16384,
    ):
        super().__init__(model, temperature, max_tokens)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.ANTHROPIC

    async def chat(
        self,
        messages: list[Message],
        system: Optional[str] = None,
        tools: Optional[list[ToolDefinition]] = None,
    ) -> LLMResponse:
        """Send chat completion to Anthropic."""
        # Convert messages to Anthropic format
        anthropic_messages = self._convert_messages(messages)

        # Build request
        request_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": anthropic_messages,
        }

        if system:
            request_kwargs["system"] = system

        if tools:
            request_kwargs["tools"] = [t.to_anthropic_format() for t in tools]

        # Make API call
        response = await self.client.messages.create(**request_kwargs)

        # Parse response
        return self._parse_response(response)

    def _convert_messages(self, messages: list[Message]) -> list[dict]:
        """Convert unified messages to Anthropic format."""
        result = []

        for msg in messages:
            if msg.role == "user":
                result.append({"role": "user", "content": msg.content})

            elif msg.role == "assistant":
                content = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments,
                    })
                # If no content, add empty text to avoid API error
                if not content:
                    content.append({"type": "text", "text": ""})
                result.append({"role": "assistant", "content": content})

            elif msg.role == "tool_result":
                content = []
                for tr in msg.tool_results:
                    item = {
                        "type": "tool_result",
                        "tool_use_id": tr.tool_call_id,
                        "content": tr.content,
                    }
                    if tr.is_error:
                        item["is_error"] = True
                    content.append(item)
                result.append({"role": "user", "content": content})

        return result

    def _parse_response(self, response) -> LLMResponse:
        """Parse Anthropic response to unified format."""
        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        )
