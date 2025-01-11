from typing import Any, Optional
import json
import redis
from datetime import timedelta

class RedisCache:
    """Implementación de caché usando Redis."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Almacena un valor en caché."""
        serialized_value = json.dumps(value)
        if ttl:
            self.redis.setex(key, timedelta(seconds=ttl), serialized_value)
        else:
            self.redis.set(key, serialized_value)
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera un valor de la caché."""
        value = self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)
    
    def delete(self, key: str) -> None:
        """Elimina un valor de la caché."""
        self.redis.delete(key)
    
    def flush(self) -> None:
        """Limpia toda la caché."""
        self.redis.flushdb() 