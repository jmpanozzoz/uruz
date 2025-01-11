from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class Message:
    """Representa un mensaje entre agentes."""
    
    id: str
    sender_id: str
    receiver_id: str
    content: Dict[str, Any]
    timestamp: datetime
    type: str
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, sender_id: str, receiver_id: str, content: Dict[str, Any], type: str = "text"):
        """Crea un nuevo mensaje."""
        return cls(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            timestamp=datetime.utcnow(),
            type=type
        )

class MessageBroker:
    """Gestiona el enrutamiento de mensajes entre agentes."""
    
    def __init__(self):
        self.subscribers = {}
    
    async def publish(self, message: Message) -> None:
        """Publica un mensaje para su entrega."""
        if message.receiver_id in self.subscribers:
            await self.subscribers[message.receiver_id](message)
    
    def subscribe(self, agent_id: str, callback):
        """Suscribe un agente para recibir mensajes."""
        self.subscribers[agent_id] = callback
    
    def unsubscribe(self, agent_id: str):
        """Cancela la suscripción de un agente."""
        if agent_id in self.subscribers:
            del self.subscribers[agent_id] 