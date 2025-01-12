"""
Ejemplo de un agente simple que responde mensajes usando un template predefinido.
"""

import asyncio
from uruz.core.environment import Environment
from uruz.core.agent import Agent

class SimpleAgent(Agent):
    """Un agente simple que responde con un mensaje predefinido."""
    
    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config)
        self.template = config.get("template", "Hola, soy {name}. {message}")
    
    async def process_message(self, message: dict) -> dict:
        """Procesa un mensaje usando el template configurado."""
        response = self.template.format(
            name=self.name,
            message=message.get("content", "")
        )
        return {"response": response}
    
    async def act(self) -> list:
        """El agente no realiza acciones autónomas."""
        return [{"status": "active"}]

async def main():
    # 1. Inicializar entorno
    env = Environment()
    
    # 2. Configurar agente
    agent_config = {
        "template": "¡Hola! Soy {name} y recibí tu mensaje: {message}"
    }
    
    # 3. Crear y registrar agente
    agent = SimpleAgent("saludador", config=agent_config)
    env.add_agent(agent)
    
    # 4. Enviar mensaje al agente
    response = await agent.process_message({
        "content": "¿Cómo estás?"
    })
    
    print("\nRespuesta del agente:")
    print(response["response"])
    
    # 5. Ejecutar ciclo del entorno
    results = await env.step()
    print("\nEstado del agente:")
    print(results)

if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de agente simple...")
    asyncio.run(main())
    print("\n✨ Ejemplo completado exitosamente!") 