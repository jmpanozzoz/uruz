from typing import Dict, Any, List, Optional, AsyncGenerator
import openai
from .base import LLMProvider
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """Implementación del proveedor de OpenAI."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        openai.api_key = config["api_key"]
        self.model = config.get("model", "gpt-4")
        
    async def generate(self, prompt: str) -> str:
        """Genera una respuesta usando OpenAI."""
        try:
            # Intentar obtener respuesta cacheada
            cached_response = self._get_cached_response(prompt)
            if cached_response:
                return cached_response
                
            # Generar nueva respuesta
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            result = response.choices[0].message.content
            
            # Cachear la respuesta
            self._cache_response(prompt, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando respuesta con OpenAI: {e}")
            raise
        
    async def embed(self, text: str) -> List[float]:
        response = await openai.Embedding.acreate(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
        
    async def stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
            **kwargs
        )
        
        async for chunk in response:
            if chunk and chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content 