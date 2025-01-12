"""
Ejemplo de un agente que utiliza un modelo de lenguaje (LLM) para procesar mensajes.
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
    
    # 3. Configurar agente LLM
    agent_config = {
        "name": "experto_python",
        "type": "llm",
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 2000,
        "temperature": 0.7,
        "system_prompt": """Eres un experto en Python que ayuda a programadores.
        Tus respuestas deben ser concisas y mostrar ejemplos de código cuando sea relevante."""
    }
    
    # 4. Registrar agente
    agent = await env.register_agent(agent_config)
    
    # 5. Enviar mensajes al agente
    preguntas = [
        "¿Cómo se manejan las excepciones en Python?",
        "¿Cuál es la diferencia entre una lista y una tupla?",
        "Muestra un ejemplo de decorador personalizado"
    ]
    
    print("\nIniciando conversación con el agente...")
    for pregunta in preguntas:
        print(f"\n🤔 Pregunta: {pregunta}")
        response = await agent.process_message({"content": pregunta})
        print(f"\n🤖 Respuesta: {response['response']}")
    
    # 6. Obtener métricas
    metrics = env.get_metrics(agent.name)
    print("\n📊 Métricas del agente:")
    print(f"- Mensajes procesados: {metrics['processed_messages']}")
    print(f"- Tokens consumidos: {metrics['total_tokens']}")
    print(f"- Tiempo promedio de respuesta: {metrics['avg_response_time']:.2f}s")

if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de agente LLM...")
    asyncio.run(main())
    print("\n✨ Ejemplo completado exitosamente!") 