from typing import Dict, List, Optional
from .agent import Agent

class Environment:
    """Entorno para gestionar múltiples agentes."""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
    
    def add_agent(self, agent: Agent) -> None:
        """Agregar un agente al entorno."""
        self._agents[agent.agent_id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Obtener un agente por su ID."""
        return self._agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """Listar todos los agentes activos."""
        return list(self._agents.keys())
    
    def remove_agent(self, agent_id: str) -> None:
        """Eliminar un agente del entorno."""
        if agent_id in self._agents:
            del self._agents[agent_id]
    
    async def step(self) -> List[dict]:
        """Ejecutar un paso de simulación para todos los agentes."""
        results = []
        for agent in self._agents.values():
            result = await agent.act()
            results.extend(result)
        return results
    
    def get_state(self) -> dict:
        """Obtener el estado actual del entorno."""
        return {
            "agents": {
                agent_id: {
                    "type": agent.__class__.__name__,
                    "status": "active"
                }
                for agent_id, agent in self._agents.items()
            },
            "total_agents": len(self._agents)
        } 