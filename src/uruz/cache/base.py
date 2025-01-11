from abc import ABC, abstractmethod
from typing import Any, Optional

class CacheProvider(ABC):
    """Interfaz base para proveedores de caché."""
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena un valor en caché."""
        pass
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Recupera un valor de la caché."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Elimina un valor de la caché."""
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """Limpia toda la caché."""
        pass 