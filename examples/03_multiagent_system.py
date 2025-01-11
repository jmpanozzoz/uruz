"""
Ejemplo 3: Sistema Multiagente
Este ejemplo muestra cómo crear un sistema con múltiples agentes que interactúan entre sí.
"""

import asyncio
from uruz.core.agent import Agent
from uruz.core.environment import Environment
from uruz.core.message import Message
from uruz.llm.openai_provider import OpenAIProvider

class ResearchAgent(Agent):
    """Agente que busca información."""
    async def process_message(self, message):
        if message.type == "query":
            # Simular búsqueda de información
            return {
                "type": "research_result",
                "data": f"Información encontrada sobre: {message.content['topic']}"
            }
        return {"type": "error", "message": "Tipo de mensaje no soportado"}

class WriterAgent(Agent):
    """Agente que escribe contenido."""
    def __init__(self, agent_id: str, config: dict):
        super().__init__(agent_id, config)
        self.llm = OpenAIProvider(config["llm_config"])
    
    async def process_message(self, message):
        if message.type == "research_result":
            # Usar LLM para escribir contenido basado en la investigación
            prompt = f"Escribe un artículo basado en: {message.content['data']}"
            content = await self.llm.generate(prompt)
            return {
                "type": "article",
                "content": content
            }
        return {"type": "error", "message": "Tipo de mensaje no soportado"}

class EditorAgent(Agent):
    """Agente que revisa y edita contenido."""
    async def process_message(self, message):
        if message.type == "article":
            # Simular edición de contenido
            return {
                "type": "final_article",
                "content": f"Artículo revisado y editado: {message.content['content']}"
            }
        return {"type": "error", "message": "Tipo de mensaje no soportado"}

async def main():
    # Crear entorno
    env = Environment()
    
    # Crear agentes
    researcher = ResearchAgent("researcher", {})
    writer = WriterAgent("writer", {
        "llm_config": {
            "api_key": "tu-api-key-aquí",
            "model": "gpt-4"
        }
    })
    editor = EditorAgent("editor", {})
    
    # Agregar agentes al entorno
    env.add_agent(researcher)
    env.add_agent(writer)
    env.add_agent(editor)
    
    # Iniciar proceso de creación de contenido
    # 1. Investigación
    research_msg = Message.create(
        sender_id="system",
        receiver_id="researcher",
        content={"topic": "Inteligencia Artificial"},
        type="query"
    )
    research_result = await env.message_broker.publish(research_msg)
    
    # 2. Escritura
    write_msg = Message.create(
        sender_id="researcher",
        receiver_id="writer",
        content=research_result,
        type="research_result"
    )
    article = await env.message_broker.publish(write_msg)
    
    # 3. Edición
    edit_msg = Message.create(
        sender_id="writer",
        receiver_id="editor",
        content=article,
        type="article"
    )
    final_article = await env.message_broker.publish(edit_msg)
    
    print("Artículo final:", final_article["content"])

if __name__ == "__main__":
    asyncio.run(main()) 