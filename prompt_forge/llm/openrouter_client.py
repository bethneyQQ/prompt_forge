"""OpenRouter (OpenAI-compatible) client implementation."""

import json
from typing import Optional

from openai import AsyncOpenAI

from .base import BaseLLMClient, LLMResponse, LLMProvider
from .message_types import Message, ToolCall
from .tool_types import ToolDefinition


class OpenRouterClient(BaseLLMClient):
    """Client for OpenRouter's OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-opus-4.5",
        temperature: float = 0.3,
        max_tokens: int = 16384,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        super().__init__(model, temperature, max_tokens)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.OPENROUTER

    async def chat(
        self,
        messages: list[Message],
        system: Optional[str] = None,
        tools: Optional[list[ToolDefinition]] = None,
    ) -> LLMResponse:
        """Send chat completion to OpenRouter."""
        # Convert messages to OpenAI format
        openai_messages = self._convert_messages(messages, system)

        # Build request
        request_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": openai_messages,
        }

        if tools:
            request_kwargs["tools"] = [t.to_openai_format() for t in tools]
            request_kwargs["tool_choice"] = "auto"

        # Make API call
        response = await self.client.chat.completions.create(**request_kwargs)

        # Parse response
        return self._parse_response(response)

    def _convert_messages(
        self,
        messages: list[Message],
        system: Optional[str]
    ) -> list[dict]:
        """Convert unified messages to OpenAI format."""
        result = []

        # Add system message first
        if system:
            result.append({"role": "system", "content": system})

        for msg in messages:
            if msg.role == "user":
                result.append({"role": "user", "content": msg.content})

            elif msg.role == "assistant":
                msg_dict = {"role": "assistant"}
                if msg.content:
                    msg_dict["content"] = msg.content
                if msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments),
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                result.append(msg_dict)

            elif msg.role == "tool_result":
                for tr in msg.tool_results:
                    result.append({
                        "role": "tool",
                        "tool_call_id": tr.tool_call_id,
                        "content": tr.content,
                    })

        return result

    def _parse_response(self, response) -> LLMResponse:
        """Parse OpenAI response to unified format."""
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            stop_reason=choice.finish_reason,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            } if response.usage else None
        )
