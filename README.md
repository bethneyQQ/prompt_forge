# Prompt Forge

A prompt optimization system that adapts your prompts for different AI providers. 

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Anthropic SDK](https://img.shields.io/badge/Anthropic-SDK-orange)](https://docs.anthropic.com/en/docs/sdks)
[![OpenAI SDK](https://img.shields.io/badge/OpenAI-SDK-blue)](https://platform.openai.com/docs)

```

## Adding New Providers

Providers are **auto-detected** from `docs/`. To add one:

```bash
# 1. Create provider directory
mkdir prompt_forge/docs/mistral

# 2. Add documentation (scrape from official docs)
cat > prompt_forge/docs/mistral/prompting.md << 'EOF'
# Mistral Prompting Guidelines

## Best Practices
- Use clear, structured instructions
- Mistral models respond well to...
EOF

# 3. Restart server - new provider appears automatically
```

The agent will now:
1. `list_provider_docs("mistral")` → `["prompting.md"]`
2. `read_provider_doc("mistral", "prompting.md")` → Full guidelines
3. Apply Mistral-specific patterns to optimize prompts

## Automatic Documentation Updates

The `updater/` directory contains an autonomous agent that automatically updates prompting guides by scraping provider documentation using **Firecrawl** and synthesizing content with **Claude Opus**.

### Updater Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler (Weekly)                        │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Claude Opus (Anthropic SDK)                 │    │
│  │         Native Tool Calling + ReAct Loop            │    │
│  │                                                     │    │
│  │  Tools:                                             │    │
│  │  • list_providers → Get configured providers        │    │
│  │  • batch_scrape_urls (Firecrawl) → Fetch all docs   │    │
│  │  • read_current_guide → Compare with existing       │    │
│  │  • update_guide → Write synthesized content         │    │
│  │  • write_update_log → Record update status          │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│              prompt_forge/docs/*.md                        │
└─────────────────────────────────────────────────────────────┘
```

### Configuration

Add URLs for new providers in `updater/config.py`:

```python
PROVIDER_CONFIGS = {
    "mistral": {
        "name": "Mistral",
        "urls": ["https://docs.mistral.ai/capabilities/completion/"],
        "doc_file": "prompting.md"
    }
}

CLAUDE_MODEL = "claude-opus-4-5-20251101"  # Model for synthesis
MAX_TURNS = 5  # Max agent iterations
```

Requires `ANTHROPIC_API_KEY` and `FIRECRAWL_API_KEY` in `.env`.

## Setup

```bash
# Backend
cd prompt_forge
pip install -r requirements.txt
echo "OPENROUTER_API_KEY=your_key" > .env
uvicorn main:app --reload --port 8000

# Frontend
cd ui
npm install
npm start
```

## License

MIT
