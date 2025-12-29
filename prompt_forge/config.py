"""Configuration for LLM providers and application settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# LLM Provider Configuration
# =============================================================================

# Provider selection: "anthropic", "openrouter", or "dashscope"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# OpenRouter settings
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# DashScope settings
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Model configuration
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "anthropic/claude-opus-4.5")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5-20251101")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-max")
FALLBACK_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

# Model parameters
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "16384"))

# Application settings
DOCS_BASE_PATH = os.path.join(os.path.dirname(__file__), "docs")


def get_llm_provider() -> str:
    """Get the configured LLM provider."""
    return LLM_PROVIDER


def get_api_key(provider: str | None = None) -> str:
    """Get API key for the specified provider."""
    provider = provider or LLM_PROVIDER
    if provider == "anthropic":
        return ANTHROPIC_API_KEY
    elif provider == "openrouter":
        return OPENROUTER_API_KEY
    elif provider == "dashscope":
        return DASHSCOPE_API_KEY
    raise ValueError(f"Unknown provider: {provider}")


def get_model(provider: str | None = None) -> str:
    """Get the model identifier for the specified provider."""
    provider = provider or LLM_PROVIDER
    if provider == "anthropic":
        return ANTHROPIC_MODEL
    elif provider == "openrouter":
        return PRIMARY_MODEL
    elif provider == "dashscope":
        return DASHSCOPE_MODEL
    return PRIMARY_MODEL


def get_max_tokens(provider: str | None = None) -> int:
    """Get the max_tokens limit for the specified provider."""
    provider = provider or LLM_PROVIDER
    if provider == "dashscope":
        return 8192  # DashScope qwen-max limit
    return DEFAULT_MAX_TOKENS


def get_supported_providers() -> list[str]:
    """
    Dynamically detect supported providers by scanning the docs folder.
    Each subfolder in docs/ that contains at least one .md file is a provider.
    """
    docs_path = Path(DOCS_BASE_PATH)
    providers = []

    if docs_path.exists():
        for item in docs_path.iterdir():
            if item.is_dir():
                # Check if folder has at least one markdown file
                md_files = list(item.glob("*.md"))
                if md_files:
                    providers.append(item.name)

    return sorted(providers)


# Get providers dynamically
SUPPORTED_PROVIDERS = get_supported_providers()
