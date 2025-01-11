from typing import Dict, Any, Optional
import time

class MemoryCache:
    """Implementación de caché en memoria."""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Almacena un valor en caché con tiempo de expiración."""
        expiration = time.time() + (ttl or self.default_ttl)
        self.cache[key] = (value, expiration)
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera un valor de la caché si no ha expirado."""
        if key not in self.cache:
            return None
            
        value, expiration = self.cache[key]
        if time.time() > expiration:
            del self.cache[key]
            return None
            
        return value 