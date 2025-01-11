"""
Ejemplo 4: Agente Autónomo Simple
Este ejemplo muestra un agente que monitorea temperatura y actúa de forma autónoma.
"""

from uruz.core.agent import Agent
import random
from typing import Dict, List, Any
import asyncio

class TemperatureMonitorAgent(Agent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.temperature_threshold = config.get('temperature_threshold', 25)
        self.current_temperature = 20

    def simulate_temperature_reading(self) -> float:
        """Simula la lectura de un sensor de temperatura."""
        self.current_temperature += random.uniform(-0.5, 0.5)
        return self.current_temperature

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes entrantes (no es el foco principal de este ejemplo)."""
        return {"type": "response", "content": f"Temperatura actual: {self.current_temperature}°C"}

    async def act(self) -> List[Dict[str, Any]]:
        """Realiza acciones autónomas basadas en la temperatura."""
        temperature = self.simulate_temperature_reading()
        actions = []

        if temperature > self.temperature_threshold:
            actions.append({
                "type": "alert",
                "content": f"¡Alerta! Temperatura alta detectada: {temperature}°C"
            })
            actions.append({
                "type": "action",
                "content": "Activando sistema de enfriamiento"
            })
        
        return actions

async def main():
    # Configurar y ejecutar el agente
    config = {
        "temperature_threshold": 25
    }
    
    agent = TemperatureMonitorAgent("temp_monitor", config)
    
    # Simular 5 ciclos de monitoreo
    for _ in range(5):
        actions = await agent.act()
        if actions:
            print("\nAcciones tomadas:")
            for action in actions:
                print(f"- {action['content']}")
        else:
            print("\nTemperatura normal, no se requieren acciones.")
        await asyncio.sleep(1)  # Esperar 1 segundo entre lecturas

if __name__ == "__main__":
    asyncio.run(main()) 