from abc import ABC, abstractmethod
from typing import Dict, List, Any

class Agent(ABC):
    """Clase base para todos los agentes."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar un mensaje entrante."""
        pass
    
    @abstractmethod
    async def act(self) -> List[Dict[str, Any]]:
        """Realizar acciones autónomas."""
        pass 