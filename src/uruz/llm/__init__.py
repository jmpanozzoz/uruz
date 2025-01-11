from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider
}

def get_provider(name: str) -> type:
    """Obtiene el proveedor LLM por nombre."""
    return PROVIDERS.get(name) 