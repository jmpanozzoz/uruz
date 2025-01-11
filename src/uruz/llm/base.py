from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import hashlib
from ..cache.redis_provider import RedisProvider

class LLMProvider(ABC):
    """Clase base para proveedores de LLM."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = RedisProvider()
        
    def _get_cache_key(self, prompt: str) -> str:
        """Genera una clave de caché para un prompt."""
        # Incluir configuración relevante en la clave
        cache_key = f"{prompt}:{self.config.get('model')}:{self.config.get('temperature')}"
        return f"llm:response:{hashlib.md5(cache_key.encode()).hexdigest()}"
        
    def _get_cached_response(self, prompt: str) -> Optional[str]:
        """Obtiene una respuesta cacheada."""
        cache_key = self._get_cache_key(prompt)
        return self.cache.get_cache(cache_key)
        
    def _cache_response(self, prompt: str, response: str,
                       expire: int = 3600) -> None:
        """Almacena una respuesta en caché."""
        cache_key = self._get_cache_key(prompt)
        self.cache.set_cache(cache_key, response, expire)
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Genera una respuesta usando el LLM."""
        pass 