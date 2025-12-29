# Qwen Prompting Guide
Last updated: 2025-12-29

## Overview

Qwen (通义千问) is a family of large language models developed by Alibaba Cloud. When prompting Qwen models, clarity and structure are essential for optimal results. Qwen uses the ChatML format for conversations and excels at following system prompts, tool calling, and multi-turn interactions.

**Key Recommendation:** Use Instruct-tuned models (with "-Instruct" suffix) for chat interactions and specific tasks, as they are specialized to understand and execute instructions effectively.

## Key Principles

### 1. Use ChatML Format
Qwen uses the ChatML format with special control tokens for structured conversations:

```
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Hello!<|im_end|>
<|im_start|>assistant
```

**Roles:**
- `system`: Meta instructions for model behavior (defaults to "You are a helpful assistant")
- `user`: User input
- `assistant`: Model responses

### 2. Leverage System Prompts
Qwen models have been fully trained on diverse system prompts, enabling:
- **Role-playing**: Assign specific personas or expertise
- **Language style transfer**: Adjust tone and formality
- **Task setting**: Define specific objectives
- **Behavior configuration**: Control response patterns

### 3. Be Clear and Structured
- State your intent and desired outcome clearly at the beginning
- Use simple, plain language
- Order matters: describe the main subject first, then environment, then details
- Keep prompts detailed but not overloaded (1-3 sentences work well)

### 4. Use Structured Prompting
For complex tasks, use a structured template:
```
[Subject Description] + [Environmental Background] + [Style Tone] + [Aesthetic Parameters] + [Emotional Atmosphere] + [On-Screen Text]
```

## Techniques

### Chain-of-Thought Prompting
For complex reasoning tasks, guide Qwen to think step-by-step:

```
Please analyze this problem step by step:
1. First, identify the key components
2. Then, evaluate each component
3. Finally, synthesize your findings

Problem: {{PROBLEM}}
```

### ReAct Prompting for Tool Use
Qwen supports ReAct (Reasoning + Acting) patterns for agent development:

```
You have access to the following tools:
{{TOOL_DESCRIPTIONS}}

To use a tool, respond with:
Thought: [your reasoning about what to do next]
Action: [the tool to use]
Action Input: [the input to the tool]
Observation: [tool result will appear here]

Continue this pattern until you can provide a final answer.

Question: {{QUESTION}}
```

Use custom stop words (e.g., "Observation:") to guide multi-step reasoning.

### Function Calling
Qwen-Chat models achieve high tool selection accuracy (98.2% on Qwen-72B-Chat). For function calling:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]
```

### Multimodal Prompting
Qwen supports multimodal inputs (text, images, audio, video). For image analysis:

```
<image>{{IMAGE_URL}}</image>
Describe what you see in this image in detail.
```

### Code Interpreter Mode
Qwen can function as a Python code interpreter:

```
You are a Python code interpreter. Execute the following code and return the result:

```python
{{CODE}}
```

Show both the code execution process and the final output.
```

## Examples

### Example 1: Role-Based System Prompt

```python
messages = [
    {"role": "system", "content": "You are an expert Python developer with 10 years of experience. Provide concise, production-ready code with brief explanations."},
    {"role": "user", "content": "Write a function to validate email addresses using regex."}
]
```

### Example 2: Structured Data Extraction

```python
messages = [
    {"role": "system", "content": "You are a data extraction assistant. Output only valid JSON."},
    {"role": "user", "content": """Extract the following information from this text:

Text: "John Smith, age 35, works at Alibaba Cloud as a senior engineer. Contact: john.smith@alibaba.com"

Extract: name, age, company, role, email

Output as JSON."""}
]
```

### Example 3: Multi-Turn Conversation

```python
messages = [
    {"role": "system", "content": "You are a helpful coding tutor."},
    {"role": "user", "content": "What is recursion?"},
    {"role": "assistant", "content": "Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem..."},
    {"role": "user", "content": "Can you show me an example with factorial?"}
]
```

## Model-Specific Guidance

### Qwen3 Series (2025)
- **Qwen3-235B-A22B**: Best for general-purpose applications requiring reasoning and efficiency
- **Qwen3-Coder-480B-A35B-Instruct**: Optimal for software development and coding tasks
- **QwQ-32B**: Best for mathematical reasoning and analytical tasks

### Context Window
- Qwen2 processes up to 32,768 tokens during training
- Plan for approximately 1 token = 3-4 characters (English) or 1.5-1.8 characters (Chinese)

### Token Handling
Be mindful of special tokens when fine-tuning. Qwen's tiktoken-based tokenizer differs from sentence-piece alternatives.

## Tips

### Do's
- Use Instruct-tuned models for chat and task completion
- Leverage system prompts for role assignment and behavior control
- Use ChatML format with proper control tokens
- Structure complex prompts with clear sections
- Use ReAct patterns for agent and tool-use scenarios
- Provide examples for consistent output formatting
- Test with Chinese and English—Qwen handles both well

### Don'ts
- Don't use base models for chat interactions (use -Instruct variants)
- Don't ignore special token handling in custom implementations
- Don't overload prompts with excessive details
- Don't mix languages mid-prompt without clear separation
- Don't skip system prompts when role-specific behavior is needed
- Don't assume default context limits—verify for your specific model

### Common Pitfalls
1. **Wrong model variant**: Using base models instead of Instruct models for conversations
2. **Token miscounting**: Not accounting for Chinese character tokenization differences
3. **Missing system prompt**: Not leveraging Qwen's strong system prompt following
4. **Unstructured tool calls**: Not using ReAct patterns for complex agent tasks
5. **Format inconsistency**: Not specifying output format explicitly when needed
