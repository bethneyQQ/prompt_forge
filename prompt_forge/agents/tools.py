"""Tool definitions and execution for the optimizer agent."""

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DOCS_BASE_PATH, SUPPORTED_PROVIDERS
from llm import ToolDefinition, ToolParameter


# =============================================================================
# Tool Definitions (for LLM)
# =============================================================================

OPTIMIZER_TOOLS = [
    ToolDefinition(
        name="list_provider_docs",
        description="List available documentation files for a provider. Call this first to see what docs are available.",
        parameters=[
            ToolParameter(
                name="provider",
                type="string",
                description="The provider name (e.g., 'openai', 'anthropic', 'google', 'kimi')"
            )
        ]
    ),
    ToolDefinition(
        name="read_provider_doc",
        description="Read a specific documentation file for a provider. Use this to read prompting guidelines.",
        parameters=[
            ToolParameter(
                name="provider",
                type="string",
                description="The provider name"
            ),
            ToolParameter(
                name="doc_name",
                type="string",
                description="The document filename (e.g., 'prompting.md')"
            )
        ]
    ),
    ToolDefinition(
        name="submit_optimization",
        description="Submit the final optimized prompt. Call this when you have read the guidelines and are ready to submit.",
        parameters=[
            ToolParameter(
                name="optimized_prompt",
                type="string",
                description="The complete optimized prompt text"
            ),
            ToolParameter(
                name="changes",
                type="array",
                description="List of changes made to the prompt",
                items={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Change category (e.g., 'structure', 'clarity', 'formatting')"},
                        "description": {"type": "string", "description": "Description of what was changed"}
                    }
                }
            )
        ]
    ),
]


# =============================================================================
# Tool Implementations
# =============================================================================

def list_provider_docs(provider: str) -> str:
    """List available documentation files for a provider."""
    provider_path = Path(DOCS_BASE_PATH) / provider.lower()

    if not provider_path.exists():
        return f"Error: Provider '{provider}' not found. Available providers: {SUPPORTED_PROVIDERS}"

    files = [f.name for f in provider_path.iterdir() if f.suffix == ".md"]

    if not files:
        return f"No documentation found for '{provider}'."

    return f"Available docs for {provider.upper()}: {', '.join(sorted(files))}. Call read_provider_doc to read them."


def read_provider_doc(provider: str, doc_name: str) -> str:
    """Read a specific documentation file for a provider."""
    if not doc_name.endswith(".md"):
        doc_name = f"{doc_name}.md"

    doc_path = Path(DOCS_BASE_PATH) / provider.lower() / doc_name

    if not doc_path.exists():
        provider_path = Path(DOCS_BASE_PATH) / provider.lower()
        if provider_path.exists():
            available = [f.name for f in provider_path.iterdir() if f.suffix == ".md"]
            return f"Document '{doc_name}' not found. Available files: {available}"
        return f"Provider '{provider}' not found. Available: {SUPPORTED_PROVIDERS}"

    content = doc_path.read_text()
    if len(content) > 12000:
        content = content[:12000] + "\n\n[Truncated - apply the patterns you've learned]"

    return f"=== {provider.upper()}: {doc_name} ===\n\n{content}"


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name with given arguments."""
    if name == "list_provider_docs":
        return list_provider_docs(args.get("provider", ""))
    elif name == "read_provider_doc":
        return read_provider_doc(
            args.get("provider", ""),
            args.get("doc_name", "")
        )
    elif name == "submit_optimization":
        # submit_optimization is handled specially in the agent loop
        return "SUBMIT"
    return f"Unknown tool: {name}"
