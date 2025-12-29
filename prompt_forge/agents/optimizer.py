"""
Optimizer agent for single-provider prompt optimization.

This is a TRUE AGENTIC implementation using native SDK tool calling.
The agent autonomously decides which documentation to read using tools,
then applies the guidelines to optimize the prompt.

Supports both Anthropic SDK (direct) and OpenRouter (via OpenAI SDK).

Includes comprehensive logging of all agent activity.
Logs are saved to: prompt_forge/logs/
"""

import json
from typing import Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import (
    create_llm_client,
    BaseLLMClient,
    LLMProvider,
    Message,
    ToolResult,
)
from config import (
    get_llm_provider,
    get_api_key,
    get_model,
    get_max_tokens,
    DEFAULT_TEMPERATURE,
)
from models.schemas import OptimizedPrompt, PromptChange
from utils.logger import FileLogger
from agents.tools import OPTIMIZER_TOOLS, execute_tool


# =============================================================================
# AGENT LOG - Captures all agent activity
# =============================================================================

class AgentLog:
    """Captures detailed logs of agent execution."""

    def __init__(self, provider: str):
        self.provider = provider
        self.entries = []
        self.start_time = datetime.now()

    def log(self, event_type: str, content: str, metadata: dict = None):
        """Add a log entry."""
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "type": event_type,
            "content": content[:500] if len(content) > 500 else content,
            "full_content": content,
            "metadata": metadata or {}
        })

    def to_dict(self) -> list:
        """Return logs as list of dicts (without full_content for API response)."""
        return [{
            "timestamp": e["timestamp"],
            "elapsed_ms": e["elapsed_ms"],
            "type": e["type"],
            "content": e["content"],
            "metadata": e["metadata"]
        } for e in self.entries]


# =============================================================================
# AGENT SYSTEM PROMPT
# =============================================================================

AGENT_SYSTEM_PROMPT = """You are a prompt optimization expert. You have access to tools to read documentation and submit your optimized prompt.

## YOUR WORKFLOW

1. Call list_provider_docs to see available docs for the target provider
2. Call read_provider_doc to read the prompting guidelines
3. Study the guidelines carefully
4. Call submit_optimization with your optimized prompt and changes

## RULES

- You MUST read documentation before optimizing
- Write the ACTUAL optimized prompt, not placeholders like "<optimized_prompt_here>"
- List SPECIFIC changes you made in the changes array
- Each change should describe: what was changed, why, based on which guideline

START by listing docs for the target provider."""


# =============================================================================
# OPTIMIZER AGENT CLASS
# =============================================================================

class OptimizerAgent:
    """Agentic optimizer that uses tools to read documentation and optimize prompts."""

    def __init__(self, provider: LLMProvider | str | None = None):
        """
        Initialize optimizer with configurable LLM provider.

        Args:
            provider: "anthropic" or "openrouter" (defaults to config)
        """
        llm_provider = provider or get_llm_provider()
        api_key = get_api_key(llm_provider)
        model = get_model(llm_provider)

        self.llm: BaseLLMClient = create_llm_client(
            provider=llm_provider,
            api_key=api_key,
            model=model,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=get_max_tokens(llm_provider),
        )

    async def optimize(
        self,
        prompt: str,
        provider: str,
        preserve_structure: bool = True,
    ) -> OptimizedPrompt:
        """Run agentic optimization with native tool calls."""
        log = AgentLog(provider)
        file_log = FileLogger(provider)

        try:
            log.log("system", f"Starting optimization for {provider.upper()}", {
                "original_prompt_length": len(prompt),
                "model": self.llm.model,
                "llm_provider": self.llm.provider.value,
            })
            file_log.log("system", f"Starting optimization for {provider.upper()}\nModel: {self.llm.model}\nLLM Provider: {self.llm.provider.value}\nOriginal prompt length: {len(prompt)} chars")

            task = f"""## TASK: Optimize for {provider.upper()}

ORIGINAL PROMPT:
```
{prompt}
```

Length: {len(prompt)} chars

## STEPS
1. Call list_provider_docs with provider={provider}
2. Call read_provider_doc to read prompting.md
3. Read and understand the guidelines
4. Call submit_optimization with your result

BEGIN NOW."""

            log.log("input", f"Task assigned to agent", {"task_length": len(task)})
            file_log.log("task_input", task)

            result = await self._run_agent_loop(task, provider, prompt, log, file_log)

            # Attach logs to result
            result.agent_logs = log.to_dict()

            log.log("complete", f"Optimization finished", {
                "success": result.success,
                "changes_count": len(result.changes),
                "output_length": len(result.prompt)
            })

            # Close file log
            file_log.close(
                success=result.success,
                result_summary=f"Changes: {len(result.changes)}\nOutput Length: {len(result.prompt)} chars"
            )

            return result

        except Exception as e:
            log.log("error", str(e))
            file_log.log("error", str(e))
            file_log.close(success=False, result_summary=f"Error: {str(e)}")

            result = OptimizedPrompt(
                provider=provider,
                prompt=prompt,
                changes=[PromptChange(category="error", description=str(e))],
                success=False,
                error=str(e),
            )
            result.agent_logs = log.to_dict()
            return result

    async def _run_agent_loop(
        self,
        task: str,
        provider: str,
        original: str,
        log: AgentLog,
        file_log: FileLogger,
    ) -> OptimizedPrompt:
        """Run the agent loop with native tool calls."""
        messages = [Message.user(task)]

        # Log the full system prompt and task
        file_log.log("system_prompt", AGENT_SYSTEM_PROMPT)

        docs_read = []
        max_iterations = 8

        for iteration in range(max_iterations):
            log.log("llm_call", f"Iteration {iteration + 1}: Calling LLM", {"iteration": iteration + 1})
            file_log.log("llm_call", f"=== ITERATION {iteration + 1} ===\n\nSending {len(messages)} messages to LLM")

            # Make LLM call with tools
            response = await self.llm.chat(
                messages=messages,
                system=AGENT_SYSTEM_PROMPT,
                tools=OPTIMIZER_TOOLS,
            )

            log.log("llm_response", response.content[:300] + "..." if len(response.content) > 300 else response.content, {
                "response_length": len(response.content),
                "tool_calls_count": len(response.tool_calls),
                "iteration": iteration + 1
            })
            file_log.log("llm_response", f"Content: {response.content}\nTool calls: {len(response.tool_calls)}\nStop reason: {response.stop_reason}")

            # Handle tool calls
            if response.tool_calls:
                # Add assistant message with tool calls
                messages.append(Message.assistant(
                    content=response.content,
                    tool_calls=response.tool_calls
                ))

                # Execute tools and collect results
                tool_results = []
                for tool_call in response.tool_calls:
                    log.log("tool_call", f"Calling: {tool_call.name}", tool_call.arguments)
                    file_log.log("tool_call", f"Tool: {tool_call.name}\nArgs: {json.dumps(tool_call.arguments, indent=2)}")

                    # Check for submission
                    if tool_call.name == "submit_optimization":
                        return self._handle_submission(
                            tool_call.arguments,
                            provider,
                            original,
                            docs_read,
                            log
                        )

                    # Execute other tools
                    result = execute_tool(tool_call.name, tool_call.arguments)

                    log.log("tool_result", result[:300] + "..." if len(result) > 300 else result, {
                        "tool": tool_call.name,
                        "result_length": len(result)
                    })
                    file_log.log("tool_result", f"Tool: {tool_call.name}\nResult ({len(result)} chars):\n{result}")

                    # Track docs read
                    if tool_call.name == "read_provider_doc":
                        doc_key = f"{tool_call.arguments.get('provider', '')}/{tool_call.arguments.get('doc_name', '')}"
                        docs_read.append(doc_key)

                    tool_results.append(ToolResult(
                        tool_call_id=tool_call.id,
                        content=result,
                    ))

                # Add tool results
                messages.append(Message.tool_result(tool_results))

            # Check if conversation ended without tool call
            elif response.stop_reason in ("end_turn", "stop"):
                log.log("warning", "LLM ended without submitting - prompting to use tools")
                file_log.log("warning", f"LLM ended with stop_reason={response.stop_reason} without tool call")
                messages.append(Message.assistant(content=response.content))
                messages.append(Message.user(
                    "Please use the submit_optimization tool to submit your optimized prompt."
                ))

        # Max iterations reached
        log.log("error", "Max iterations reached without completion")
        return OptimizedPrompt(
            provider=provider,
            prompt=original,
            changes=[PromptChange(category="error", description="Optimization did not complete")],
            success=False,
            error="Max iterations reached",
        )

    def _handle_submission(
        self,
        args: dict,
        provider: str,
        original: str,
        docs_read: list,
        log: AgentLog,
    ) -> OptimizedPrompt:
        """Handle the submit_optimization tool call."""
        optimized = args.get("optimized_prompt", "")
        changes_data = args.get("changes", [])

        # Validate submission
        if not optimized or len(optimized) < 15:
            log.log("parse_error", "Empty or too short optimized prompt")
            return OptimizedPrompt(
                provider=provider,
                prompt=original,
                changes=[PromptChange(category="error", description="Empty optimization submitted")],
                success=False,
                error="Empty or too short output",
            )

        # Check for placeholder patterns
        invalid_patterns = [
            "<optimized_prompt_here>",
            "[your prompt here]",
            "placeholder",
            "insert your",
        ]
        optimized_lower = optimized.lower().strip()
        for pattern in invalid_patterns:
            if pattern in optimized_lower:
                log.log("parse_error", f"Placeholder detected: {pattern}")
                return OptimizedPrompt(
                    provider=provider,
                    prompt=original,
                    changes=[PromptChange(category="error", description="Agent submitted placeholder")],
                    success=False,
                    error="Placeholder output detected",
                )

        # Parse changes
        changes = []
        for change in changes_data:
            if isinstance(change, dict):
                changes.append(PromptChange(
                    category=change.get("category", "optimization"),
                    description=change.get("description", "Applied optimization"),
                ))

        # Fallback if no changes provided
        if not changes:
            for doc in docs_read:
                changes.append(PromptChange(
                    category="provider_pattern",
                    description=f"Applied guidelines from {doc}"
                ))
            if not changes:
                changes.append(PromptChange(
                    category="optimization",
                    description=f"Optimized for {provider.upper()}"
                ))

        log.log("submit", f"Optimization submitted ({len(optimized)} chars, {len(changes)} changes)")

        return OptimizedPrompt(
            provider=provider,
            prompt=optimized,
            changes=changes,
            success=True,
        )
