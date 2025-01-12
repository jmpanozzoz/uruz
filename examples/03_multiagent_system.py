"""
Ejemplo de un sistema multiagente donde varios agentes colaboran para resolver una tarea.
"""

import asyncio
from uruz.core.environment import Environment
from uruz.security.vault import Vault

async def main():
    # 1. Configurar credenciales
    vault = Vault()
    vault.store_credential("openai_api_key", "tu-api-key-aqui")
    
    # 2. Inicializar entorno
    env = Environment()
    
    # 3. Configurar agentes
    agentes = [
        {
            "name": "arquitecto",
            "type": "llm",
            "provider": "openai",
            "model": "gpt-4",
            "system_prompt": """Eres un arquitecto de software experto.
            Tu rol es diseñar la estructura de alto nivel de los sistemas."""
        },
        {
            "name": "desarrollador",
            "type": "llm",
            "provider": "openai",
            "model": "gpt-4",
            "system_prompt": """Eres un desarrollador Python experto.
            Tu rol es implementar las soluciones propuestas por el arquitecto."""
        },
        {
            "name": "tester",
            "type": "llm",
            "provider": "openai",
            "model": "gpt-4",
            "system_prompt": """Eres un tester experto.
            Tu rol es revisar el código y sugerir pruebas."""
        }
    ]
    
    # 4. Registrar agentes
    print("\n🚀 Registrando agentes...")
    registered_agents = {}
    for config in agentes:
        agent = await env.register_agent(config)
        registered_agents[config["name"]] = agent
        print(f"✓ Agente {config['name']} registrado")
    
    # 5. Simular proceso de desarrollo
    print("\n🔄 Iniciando proceso de desarrollo...")
    
    # 5.1 Arquitecto diseña
    print("\n👷 Arquitecto diseñando...")
    response = await registered_agents["arquitecto"].process_message({
        "content": """Diseña un sistema simple para gestionar una biblioteca.
        Debe permitir agregar/eliminar libros y gestionar préstamos."""
    })
    diseño = response["response"]
    print(f"\nDiseño propuesto:\n{diseño}")
    
    # 5.2 Desarrollador implementa
    print("\n👨‍💻 Desarrollador implementando...")
    response = await registered_agents["desarrollador"].process_message({
        "content": f"Implementa en Python el siguiente diseño:\n{diseño}"
    })
    implementacion = response["response"]
    print(f"\nImplementación:\n{implementacion}")
    
    # 5.3 Tester revisa
    print("\n🔍 Tester revisando...")
    response = await registered_agents["tester"].process_message({
        "content": f"Revisa esta implementación y sugiere pruebas:\n{implementacion}"
    })
    revision = response["response"]
    print(f"\nRevisión y pruebas sugeridas:\n{revision}")
    
    # 6. Obtener métricas
    print("\n📊 Métricas del sistema:")
    for name, agent in registered_agents.items():
        metrics = env.get_metrics(agent.name)
        print(f"\nAgente: {name}")
        print(f"- Mensajes procesados: {metrics['processed_messages']}")
        print(f"- Tokens consumidos: {metrics['total_tokens']}")
        print(f"- Tiempo promedio de respuesta: {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de sistema multiagente...")
    asyncio.run(main())
    print("\n✨ Ejemplo completado exitosamente!") 