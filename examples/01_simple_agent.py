"""
Ejemplo 1: Agente Simple
Este ejemplo muestra cómo crear y usar un agente básico que responde mensajes.
"""

import asyncio
from uruz.core.agent import Agent
from uruz.security.vault import Vault

class SimpleAgent(Agent):
    async def process_message(self, message):
        # Simplemente devuelve una respuesta estática
        return {
            "response": f"Recibido mensaje: {message['content']}"
        }
    
    async def act(self):
        # Este agente no realiza acciones autónomas
        return []

async def main():
    # Crear y configurar agente
    agent = SimpleAgent(
        agent_id="agente-simple",
        config={"name": "Asistente Básico"}
    )
    
    # Enviar un mensaje al agente
    response = await agent.process_message({
        "content": "¡Hola!"
    })
    
    print(f"Respuesta del agente: {response}")

if __name__ == "__main__":
    asyncio.run(main()) 