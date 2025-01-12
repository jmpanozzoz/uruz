"""
Prueba completa del sistema Uruz Framework.
"""

import asyncio
from uruz.core.environment import Environment
from uruz.security.vault import Vault

async def test_system():
    """Ejecuta una prueba completa del sistema."""
    
    print("\n🔧 Configurando sistema...")
    
    # 1. Configurar credenciales
    vault = Vault()
    vault.store_credential("openai_api_key", "tu-api-key-aqui")
    
    # 2. Inicializar entorno
    env = Environment()
    
    # 3. Configurar agente de prueba
    agent_config = {
        "name": "test_agent",
        "type": "llm",
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 1000,
        "temperature": 0.7,
        "system_prompt": "Eres un asistente de pruebas que verifica el funcionamiento del sistema."
    }
    
    # 4. Registrar agente
    print("\n🤖 Registrando agente de prueba...")
    agent = await env.register_agent(agent_config)
    
    # 5. Probar funcionalidades
    print("\n🔄 Probando funcionalidades...")
    
    # 5.1 Procesar mensaje
    print("\n📝 Probando procesamiento de mensajes...")
    response = await agent.process_message({
        "content": "Confirma que estás funcionando correctamente."
    })
    print(f"Respuesta: {response['response']}")
    
    # 5.2 Ejecutar ciclo del entorno
    print("\n⚡ Probando ciclo del entorno...")
    results = await env.step()
    print(f"Resultados: {results}")
    
    # 5.3 Obtener métricas
    print("\n📊 Probando métricas...")
    metrics = env.get_metrics(agent.name)
    print("Métricas del agente:")
    print(f"- Mensajes procesados: {metrics['processed_messages']}")
    print(f"- Tokens consumidos: {metrics['total_tokens']}")
    print(f"- Tiempo promedio de respuesta: {metrics['avg_response_time']:.2f}s")
    
    print("\n✅ Pruebas completadas exitosamente!")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema...")
    asyncio.run(test_system())
    print("\n✨ Sistema verificado exitosamente!") 