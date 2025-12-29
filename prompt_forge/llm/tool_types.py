"""Unified tool definition format for all LLM providers."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolParameter:
    """A parameter for a tool."""
    name: str
    type: str  # "string", "array", "object", "number", "boolean"
    description: str
    required: bool = True
    items: dict[str, Any] | None = None  # For array types
    properties: dict[str, Any] | None = None  # For object types


@dataclass
class ToolDefinition:
    """Unified tool definition that converts to provider-specific formats."""
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_anthropic_format(self) -> dict:
        """Convert to Anthropic's tool format."""
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.items:
                prop["items"] = param.items
            if param.properties:
                prop["properties"] = param.properties
            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }

    def to_openai_format(self) -> dict:
        """Convert to OpenAI's function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.items:
                prop["items"] = param.items
            if param.properties:
                prop["properties"] = param.properties
            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }
