import asyncio
from uruz.core.environment import Environment
from uruz.agents.llm_agent import LLMAgent # type: ignore

async def test_system():
    env = Environment()
    
    # Crear y registrar agente
    agent = LLMAgent(
        agent_id="test-agent",
        config={
            "api_key": "tu-api-key-aquí",
            "name": "Test Agent"
        }
    )
    env.add_agent(agent)
    
    # Probar funcionamiento
    response = await agent.process_message({
        "content": "Hola, ¿está funcionando el sistema?"
    })
    
    print("Respuesta:", response)
    
    # Verificar estado del sistema
    state = env.get_state()
    print("\nEstado del sistema:", state)

if __name__ == "__main__":
    asyncio.run(test_system()) 