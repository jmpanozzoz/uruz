from typing import Dict, Any, List
from .agent import Agent
from ..llm import get_provider

class LLMAgent(Agent):
    """Agente que usa un modelo de lenguaje."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        provider_class = get_provider(config.get("provider", "anthropic"))
        if not provider_class:
            raise ValueError(f"Provider {config.get('provider')} not found")
        self.llm = provider_class(config)
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje usando el LLM."""
        response = await self.llm.generate(message["content"])
        return {"response": response}
    
    async def act(self) -> List[Dict[str, Any]]:
        """Este agente no realiza acciones autónomas."""
        return [] 