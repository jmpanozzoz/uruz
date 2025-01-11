"""
Ejemplo 5: Agente Avanzado
Este ejemplo muestra un agente más complejo con memoria y capacidades avanzadas.
"""

import asyncio
from uruz.core.agent import Agent
from uruz.security.vault import Vault
from uruz.llm.openai_provider import OpenAIProvider
from uruz.cache.redis import RedisCache

class AdvancedAgent(Agent):
    def __init__(self, agent_id: str, config: dict):
        super().__init__(agent_id, config)
        
        # Configurar LLM
        self.llm = OpenAIProvider(config["llm_config"])
        
        # Configurar caché para memoria
        self.memory = RedisCache(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379)
        )
        
        # Estado interno
        self.conversation_history = []
    
    async def process_message(self, message):
        # Agregar mensaje a la historia
        self.conversation_history.append({
            "role": "user",
            "content": message["content"]
        })
        
        # Generar contexto con historia
        context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_history[-5:]  # Últimos 5 mensajes
        ])
        
        # Generar respuesta considerando contexto
        prompt = f"""
        Contexto de la conversación:
        {context}
        
        Responde al último mensaje de manera coherente con la conversación.
        """
        
        response = await self.llm.generate(prompt)
        
        # Guardar respuesta en historia
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Guardar en caché
        await self.memory.set(
            f"conversation_{self.agent_id}",
            self.conversation_history
        )
        
        return {"response": response}
    
    async def act(self):
        # Realizar acciones basadas en la conversación
        if len(self.conversation_history) > 0:
            last_message = self.conversation_history[-1]
            if "recordatorio" in last_message["content"].lower():
                return [{
                    "action": "create_reminder",
                    "content": last_message["content"]
                }]
        return []

async def main():
    # Configurar agente avanzado
    agent = AdvancedAgent(
        agent_id="asistente-avanzado",
        config={
            "llm_config": {
                "api_key": "tu-api-key-aquí",
                "model": "gpt-4"
            },
            "redis_host": "localhost",
            "redis_port": 6379
        }
    )
    
    # Simular conversación
    messages = [
        "¡Hola! ¿Cómo estás?",
        "Cuéntame sobre la inteligencia artificial",
        "Interesante. ¿Puedes dar un ejemplo práctico?",
        "Recordatorio: investigar más sobre machine learning mañana"
    ]
    
    for msg in messages:
        response = await agent.process_message({"content": msg})
        print(f"\nUsuario: {msg}")
        print(f"Asistente: {response['response']}")
        
        # Verificar acciones
        actions = await agent.act()
        if actions:
            print(f"Acciones: {actions}")

if __name__ == "__main__":
    asyncio.run(main()) 