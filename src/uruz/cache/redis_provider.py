import redis
from typing import Any, Optional, Dict, List
from datetime import timedelta
import json
from ..config import settings

class RedisProvider:
    """Proveedor de Redis para caché y mensajería."""
    
    def __init__(self, host: str = settings.REDIS_HOST, 
                 port: int = settings.REDIS_PORT,
                 db: int = 0):
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        
    def set_cache(self, key: str, value: Any, 
                 expire: Optional[int] = None) -> bool:
        """Almacena un valor en caché."""
        try:
            self.redis.set(
                key,
                json.dumps(value),
                ex=expire
            )
            return True
        except Exception:
            return False
            
    def get_cache(self, key: str) -> Optional[Any]:
        """Obtiene un valor de caché."""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
            
    def delete_cache(self, key: str) -> bool:
        """Elimina un valor de caché."""
        try:
            return bool(self.redis.delete(key))
        except Exception:
            return False
            
    def push_task(self, queue: str, task: Dict[str, Any]) -> bool:
        """Agrega una tarea a la cola."""
        try:
            return bool(self.redis.rpush(
                f"queue:{queue}",
                json.dumps(task)
            ))
        except Exception:
            return False
            
    def pop_task(self, queue: str) -> Optional[Dict[str, Any]]:
        """Obtiene y elimina una tarea de la cola."""
        try:
            task = self.redis.lpop(f"queue:{queue}")
            return json.loads(task) if task else None
        except Exception:
            return None
            
    def get_queue_length(self, queue: str) -> int:
        """Obtiene la longitud de una cola."""
        try:
            return self.redis.llen(f"queue:{queue}")
        except Exception:
            return 0
            
    def set_agent_state(self, agent_id: str, 
                       state: Dict[str, Any],
                       expire: int = 300) -> bool:
        """Almacena el estado de un agente."""
        try:
            return self.set_cache(
                f"agent:state:{agent_id}",
                state,
                expire
            )
        except Exception:
            return False
            
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de un agente."""
        return self.get_cache(f"agent:state:{agent_id}")
        
    def get_all_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene el estado de todos los agentes."""
        try:
            keys = self.redis.keys("agent:state:*")
            states = {}
            for key in keys:
                agent_id = key.split(":")[-1]
                state = self.get_agent_state(agent_id)
                if state:
                    states[agent_id] = state
            return states
        except Exception:
            return {}
            
    def publish_event(self, channel: str, event: Dict[str, Any]) -> bool:
        """Publica un evento en un canal."""
        try:
            return bool(self.redis.publish(
                channel,
                json.dumps(event)
            ))
        except Exception:
            return False
            
    def subscribe_to_events(self, channels: List[str]):
        """Suscribe a canales de eventos."""
        pubsub = self.redis.pubsub()
        pubsub.subscribe(*channels)
        return pubsub
        
    def clear_cache(self, pattern: str = "*") -> int:
        """Limpia la caché según un patrón."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception:
            return 0 