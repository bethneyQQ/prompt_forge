# Prompt Forge

An intelligent prompt optimization system that automatically adapts your prompts to different AI providers' best practices.

## Features

### Core Capabilities

- **Multi-platform Adaptation** - One input, multiple optimized outputs for OpenAI, Anthropic, Google, Kimi, etc.
- **Intelligent Optimization** - Agent automatically reads each platform's official prompting guidelines and applies best practices
- **Parallel Processing** - Multiple optimization tasks run simultaneously for fast results
- **Flexible Selection** - Choose single or multiple target platforms for optimization

### How It Works

```
User inputs prompt
      ↓
Select target platforms (OpenAI / Anthropic / Google / Kimi)
      ↓
Agent reads the corresponding platform's prompting guidelines
      ↓
Applies best practices for optimization
      ↓
Returns optimized prompt + change summary
```

### Supported Platforms

| Platform | Optimization Features |
|----------|----------------------|
| OpenAI | Structured system messages, Markdown formatting |
| Anthropic | XML tag structure, clear and direct instructions |
| Google | Task/format/context pattern |
| Kimi | Structured output formatting |

## Installation

### Requirements

- Python 3.11+

### Setup

```bash
# 1. Enter project directory
cd prompt_forge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp env.example .env

# 4. Edit .env file
# Choose LLM provider: anthropic or openrouter
LLM_PROVIDER=openrouter

# Enter API Key (choose one)
OPENROUTER_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Start Service

```bash
cd prompt_forge
uvicorn main:app --reload --port 8000
```

Service available at: http://localhost:8000

## Usage

### API Calls

**Optimize for single platform:**

```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "You are a helpful assistant.",
    "providers": ["openai"]
  }'
```

**Optimize for multiple platforms:**

```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "You are a helpful assistant.",
    "providers": ["openai", "anthropic", "google"]
  }'
```

**List available platforms:**

```bash
curl http://localhost:8000/providers
```

### Python

```python
import httpx

response = httpx.post("http://localhost:8000/optimize", json={
    "prompt": "You are a helpful assistant.",
    "providers": ["anthropic"]
})

result = response.json()
print(result["optimized"]["anthropic"]["prompt"])
print(result["optimized"]["anthropic"]["changes"])
```

### Response Example

```json
{
  "original": "You are a helpful assistant.",
  "optimized": {
    "openai": {
      "provider": "openai",
      "prompt": "# Role\nYou are a helpful assistant...",
      "changes": [
        {"category": "structure", "description": "Added Markdown heading structure"},
        {"category": "clarity", "description": "Clarified role definition and behavioral constraints"}
      ],
      "success": true
    }
  }
}
```

## Adding New Platforms

1. Create a new directory under `prompt_forge/docs/`
2. Add the platform's prompting guide as `prompting.md`
3. Restart the service - new platform is automatically detected

```bash
mkdir prompt_forge/docs/mistral
echo "# Mistral Prompting Guide\n..." > prompt_forge/docs/mistral/prompting.md
```

## License

MIT
