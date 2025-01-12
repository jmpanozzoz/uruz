"""
Ejemplo de inicio rápido para Uruz Framework
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
    
    # 3. Crear configuración del agente
    agent_config = {
        "name": "asistente",
        "type": "llm",
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 2000,
        "temperature": 0.7,
        "system_prompt": "Eres un asistente experto en Python."
    }
    
    # 4. Registrar agente
    agent = await env.register_agent(agent_config)
    
    # 5. Enviar mensaje al agente
    response = await agent.process_message({
        "content": "¿Cuáles son las principales características de Python?"
    })
    
    print("\nRespuesta del agente:")
    print(response["response"])
    
    # 6. Obtener métricas
    metrics = env.get_metrics(agent.name)
    print("\nMétricas del agente:")
    print(f"- Mensajes procesados: {metrics['processed_messages']}")
    print(f"- Tokens consumidos: {metrics['total_tokens']}")
    print(f"- Tiempo promedio de respuesta: {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de Uruz Framework...")
    asyncio.run(main())
    print("\n✨ Ejemplo completado exitosamente!") 