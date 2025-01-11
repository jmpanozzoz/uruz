import asyncio
from uruz.core.agent import Agent
from uruz.core.environment import Environment
from uruz.llm.openai_provider import OpenAIProvider
from uruz.security.vault import Vault
from uruz.config import settings
from uruz.utils.logging import logger

class SimpleAgent(Agent):
    async def process_message(self, message):
        logger.info(f"Procesando mensaje: {message}")
        response = await self.llm.generate(message["content"])
        return {"response": response}
    
    async def act(self):
        return [{"status": "active"}]

async def main():
    # Configurar entorno
    env = Environment()
    
    # Configurar vault y credenciales
    vault = Vault()
    vault.store_credential("openai_api_key", settings.OPENAI_API_KEY)
    
    # Configurar LLM
    llm_config = {
        "api_key": vault.get_credential("openai_api_key"),
        **settings.LLM_CONFIG
    }
    llm = OpenAIProvider(llm_config)
    
    # Crear y registrar agente
    agent = SimpleAgent("agent-1", config={"llm": llm})
    env.add_agent(agent)
    
    # Probar funcionamiento
    response = await agent.process_message({
        "content": "¿Cuál es tu función principal?"
    })
    logger.info(f"Respuesta: {response}")
    
    # Ejecutar ciclo del entorno
    results = await env.step()
    logger.info(f"Resultados del paso: {results}")

if __name__ == "__main__":
    asyncio.run(main()) 