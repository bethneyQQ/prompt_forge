# DeepSeek Prompting Guide
Last updated: 2025-12-29

## Overview

DeepSeek (深度求索) offers powerful language models with exceptional reasoning capabilities. The DeepSeek R1 series are "thinking models" that perform internal chain-of-thought reasoning, requiring a different prompting approach than traditional LLMs.

**Key Insight:** DeepSeek R1 models work best with minimal, concise prompts. Unlike traditional LLMs, they can be hindered by verbose instructions or explicit chain-of-thought guidance.

## Key Principles

### 1. Use Minimal Prompting for Reasoning Models
For DeepSeek R1 and similar thinking models:
- Use concise, direct, and structured prompts
- Avoid verbose instructions that can reduce accuracy
- State problems clearly and let the model reason independently
- Don't prescribe thinking steps—let the model find its own path

### 2. Avoid Traditional Techniques with R1
Research shows these can degrade performance on thinking models:
- **Don't use few-shot examples**: R1 performs worse with example demonstrations
- **Don't use explicit CoT prompting**: "Think step by step" can interfere with native reasoning
- **Don't over-specify**: Trust the model's internal reasoning capabilities

### 3. Be Clear and Specific
- Use strong action words: "Write," "Explain," "List," "Analyze"
- Provide context: task description, target audience, tone, format
- Specify output format if needed (JSON, markdown table, numbered list)

### 4. Break Down Complex Tasks
Rather than overwhelming with multi-part requests:
- Use sequential prompts for focused responses
- Allow each step to complete before moving to the next
- Build context iteratively

## Techniques

### Encouraging Extended Thinking
For complex problems, encourage deeper reasoning:

```
Take your time and think carefully about this problem.

{{COMPLEX_PROBLEM}}
```

**Important:** Avoid interrupting reasoning with step-by-step instructions. Let the model engage its native thinking process.

### Chain-of-Draft (CoD) for Token Efficiency
Reduce token usage by up to 80% while maintaining quality:

```
Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.

{{PROBLEM}}
```

This approach mimics taking concise notes rather than writing verbose explanations.

### Structured Output with Think/Answer Tags
For complex reasoning with clean output separation:

```
Analyze this problem and provide your solution.

Structure your response with:
<think>
[Your reasoning process]
</think>
<answer>
[Your final answer]
</answer>

Problem: {{PROBLEM}}
```

### Role-Playing Prompts
Assign expertise for domain-specific responses:

```
You are a senior software architect with expertise in distributed systems.

Review this system design and identify potential bottlenecks:
{{DESIGN}}
```

### Programming Tasks
Be specific about requirements:

```
Write a Python function that:
- Input: A list of integers
- Output: The two numbers that sum to a target value
- Requirements: O(n) time complexity, handle edge cases
- Format: Include docstring and type hints
```

### Mathematical Problem Solving
Provide clear specifications:

```
Solve this optimization problem.

Given: {{CONSTRAINTS}}
Find: {{OBJECTIVE}}

State all values clearly.
Use standard mathematical notation.
Show your work with step-by-step reasoning.
```

## Examples

### Example 1: Minimal Prompting for R1

**Don't do this:**
```
I want you to solve this math problem. Please think step by step. First, identify the variables. Then, set up the equations. Next, solve the equations. Finally, verify your answer.

What is the derivative of x^3 + 2x^2 - 5x + 3?
```

**Do this instead:**
```
Find the derivative of x^3 + 2x^2 - 5x + 3
```

### Example 2: Structured Code Review Request

```
You are a security-focused code reviewer.

Review this code for vulnerabilities:
```python
{{CODE}}
```

Identify:
1. Security issues (with severity: high/medium/low)
2. Recommended fixes
3. Best practices violations

Format as a markdown table.
```

### Example 3: Data Analysis with Clear Scope

```
Analyze this dataset for customer churn patterns.

Dataset summary:
{{DATASET_INFO}}

Focus on:
- Key predictive features
- Correlation patterns
- Actionable insights

Limit analysis to the top 5 findings.
```

### Example 4: Chain-of-Draft for Efficiency

```
Solve this logic puzzle using minimal reasoning steps (5 words max per step):

{{PUZZLE}}
```

## Model-Specific Guidance

### DeepSeek R1 (Thinking Model)
- Best for: Complex problems requiring 5+ reasoning steps
- Temperature: 0.5-0.7 for balanced creativity and coherence
- Approach: Minimal prompting, let the model think independently
- Avoid: Few-shot examples, explicit CoT instructions

### DeepSeek V3 / Chat Models
- Best for: General tasks, structured outputs, simpler problems
- Approach: Traditional prompting techniques work well
- Use: Few-shot examples, explicit formatting instructions

### When to Choose Which Model
| Task Type | Recommended Model |
|-----------|------------------|
| Complex reasoning (5+ steps) | DeepSeek R1 |
| Analytical tasks | DeepSeek R1 |
| Simple Q&A (< 3 steps) | DeepSeek V3/Chat |
| Structured output needs | DeepSeek V3/Chat |
| Tasks benefiting from examples | DeepSeek V3/Chat |

## Tips

### Do's
- Use concise, direct prompts for R1 models
- Specify output format clearly when needed
- Break complex tasks into sequential prompts
- Use strong action verbs (Write, List, Explain, Analyze)
- Encourage extended thinking for complex problems: "Take your time"
- Use Chain-of-Draft for token efficiency
- Match model to task complexity

### Don'ts
- Don't use few-shot examples with R1 (degrades performance)
- Don't prescribe step-by-step thinking for R1
- Don't overload prompts with excessive context
- Don't mix languages mid-prompt
- Don't use vague instructions like "Make it better"
- Don't expect structured outputs from thinking models
- Don't use R1 for simple tasks (it may "overthink")

### Common Pitfalls
1. **Over-prompting R1**: Verbose instructions reduce accuracy on thinking models
2. **Wrong model selection**: Using R1 for simple tasks wastes tokens and may reduce quality
3. **Forcing CoT on R1**: Explicit step-by-step instructions interfere with native reasoning
4. **Ambiguous scope**: Not defining clear boundaries for analysis or output
5. **Mixed language prompts**: Inconsistent language usage causes confusion
6. **Missing format specs**: Not specifying output structure when needed
7. **Single mega-prompt**: Trying to do too much in one request

### Temperature Settings
- **0.5-0.7**: Recommended for R1, balances creativity and coherence
- **Lower (0.1-0.3)**: For deterministic, factual outputs
- **Higher (0.8-1.0)**: For creative tasks (use with caution on R1)
