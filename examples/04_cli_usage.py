"""
Ejemplo 4: Uso de la CLI
Este ejemplo muestra diferentes formas de usar la CLI del framework.
"""

# 1. Crear un nuevo agente LLM
# uruz create-agent --name "asistente" --type llm

# 2. Crear un agente simple
# uruz create-agent --name "worker" --type simple

# 3. Iniciar el servidor en modo debug
# uruz serve --debug --port 5000

# 4. Ver estado del sistema
# uruz status --check-deps

# 5. Listar agentes activos
# uruz list-agents

# El archivo de configuración .env debe contener:
"""
DATABASE_URL=sqlite:///./uruz.db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
OPENAI_API_KEY=tu-api-key-aquí
""" 