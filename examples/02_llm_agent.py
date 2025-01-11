"""
Ejemplo 2: Agente con LLM
Este ejemplo muestra cómo crear un agente que utiliza GPT para procesar mensajes.
"""

import asyncio
from uruz.core.agent import Agent
from uruz.security.vault import Vault
from uruz.llm.openai_provider import OpenAIProvider

class LLMAgent(Agent):
    def __init__(self, agent_id: str, config: dict):
        super().__init__(agent_id, config)
        
        # Configurar LLM
        vault = Vault()
        vault.store_credential("openai_api_key", config["api_key"])
        
        llm_config = {
            "api_key": vault.get_credential("openai_api_key"),
            "model": "gpt-4",
            "temperature": 0.7
        }
        self.llm = OpenAIProvider(llm_config)
    
    async def process_message(self, message):
        # Usar LLM para generar respuesta
        prompt = f"Actúa como un asistente amigable y responde: {message['content']}"
        response = await self.llm.generate(prompt)
        return {"response": response}
    
    async def act(self):
        return []

async def main():
    # Crear agente con LLM
    agent = LLMAgent(
        agent_id="asistente-gpt",
        config={
            "api_key": "tu-api-key-aquí",
            "name": "Asistente GPT"
        }
    )
    
    # Interactuar con el agente
    response = await agent.process_message({
        "content": "¿Cuál es la capital de Francia?"
    })
    
    print(f"Respuesta: {response['response']}")

if __name__ == "__main__":
    asyncio.run(main()) 