from typing import Dict, Any
from anthropic import Anthropic
from .base import LLMProvider
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    """Proveedor de LLM usando Anthropic Claude."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Siempre usar la API key de settings
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        # Usar configuración del settings como valores por defecto
        self.model = config.get("model", settings.LLM_CONFIG["model"])
        self.max_tokens = config.get("max_tokens", settings.LLM_CONFIG["max_tokens"])
        self.temperature = config.get("temperature", settings.LLM_CONFIG["temperature"])
        self.system_prompt = config.get("system_prompt", "")
    
    async def generate(self, prompt: str) -> str:
        """Genera una respuesta usando Claude."""
        try:
            # Intentar obtener respuesta cacheada
            cached_response = self._get_cached_response(prompt)
            if cached_response:
                return cached_response
                
            # Generar nueva respuesta
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response = message.content[0].text
            
            # Cachear la respuesta
            self._cache_response(prompt, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta con Claude: {e}")
            raise 