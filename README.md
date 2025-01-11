# Uruz Framework

Uruz es un framework de sistemas multiagente con IA que permite crear, gestionar y desplegar agentes inteligentes que pueden interactuar entre sí y con servicios externos.

## 🌟 Características Principales

- **Múltiples Proveedores de IA**: Soporte para OpenAI y Anthropic (Claude)
- **Sistema de Agentes**: Crea y gestiona múltiples agentes con diferentes roles
- **Gestión Segura**: Vault integrado para almacenamiento seguro de credenciales
- **CLI Potente**: Interfaz de línea de comandos para todas las operaciones
- **API REST**: Endpoints para interactuar con los agentes
- **Caché Redis**: Optimización de respuestas y gestión de estado
- **Base de Datos**: Almacenamiento SQLite para métricas e historial
- **Logging Detallado**: Sistema de logs para monitoreo y debugging

## 📋 Requisitos

- Python 3.8+
- Redis (opcional, para caché)
- Claves API para los proveedores de IA que desees usar:
  - OpenAI: [Obtener clave](https://platform.openai.com/api-keys)
  - Anthropic: [Obtener clave](https://console.anthropic.com/account/keys)

## 🚀 Instalación

```bash
# Instalar desde PyPI
pip install uruz-framework

# O instalar en modo desarrollo
git clone https://github.com/jmpanozzoz/uruz.git
cd uruz
pip install -e .
```

## ⚙️ Configuración

1. Crea un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=tu-clave-openai
ANTHROPIC_API_KEY=tu-clave-anthropic
SSH_KEY_PATH=~/.ssh/id_rsa

# Opcional para Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

2. Inicializa el vault para credenciales:

```bash
python scripts/setup_credentials.py
```

## 🤖 Creación de Agentes

### Usando el CLI

```bash
# Crear un agente LLM con OpenAI
uruz create-agent --name mi_agente --type llm --provider openai

# Crear un agente para gestión de servidores
uruz create-agent --name servidor_agent --type server --provider anthropic
```

### Configuración Manual

Crea un archivo YAML en el directorio `agents/`:

```yaml
name: mi_agente
type: llm
provider: openai
config:
  model: gpt-3.5-turbo-1106
  temperature: 0.7
  max_tokens: 1024
  system_prompt: |
    Eres un asistente amigable y servicial.
    Siempre respondes en español.
  openai_api_key: ${OPENAI_API_KEY}
```

## 🛠 Ejemplos de Código

### Ejemplo Básico: Asistente Simple

```python
from uruz.core.llm_agent import LLMAgent
from uruz.llm.openai_provider import OpenAIProvider

# Configuración del agente
config = {
    "model": "gpt-3.5-turbo-1106",
    "temperature": 0.7,
    "max_tokens": 1024,
    "system_prompt": "Eres un asistente amigable que responde en español."
}

# Crear y usar el agente
async def main():
    # Inicializar agente
    agent = LLMAgent("asistente", config)

    # Enviar mensaje y obtener respuesta
    response = await agent.process_message({
        "content": "¿Cuál es la capital de Francia?"
    })

    print(response["response"])

# Ejecutar
import asyncio
asyncio.run(main())
```

### Ejemplo Intermedio: Agente con Memoria

```python
from uruz.core.llm_agent import LLMAgent
from uruz.storage.memory import ConversationMemory

class AgentConMemoria(LLMAgent):
    def __init__(self, agent_id: str, config: dict):
        super().__init__(agent_id, config)
        self.memory = ConversationMemory()

    async def process_message(self, message: dict) -> dict:
        # Obtener historial
        history = self.memory.get_history()

        # Crear prompt con contexto
        context = "\n".join([
            f"Usuario: {m['content']}\nAsistente: {m['response']}"
            for m in history
        ])

        prompt = f"""
        Historial de conversación:
        {context}

        Usuario: {message['content']}
        """

        # Generar respuesta
        response = await self.llm.generate(prompt)

        # Guardar en memoria
        self.memory.add_interaction(message["content"], response)

        return {"response": response}

# Uso
async def main():
    config = {
        "model": "gpt-3.5-turbo-1106",
        "temperature": 0.7,
        "max_tokens": 1024
    }

    agent = AgentConMemoria("asistente_memoria", config)

    # Primera pregunta
    resp1 = await agent.process_message({
        "content": "Mi nombre es Juan"
    })

    # Segunda pregunta (con contexto)
    resp2 = await agent.process_message({
        "content": "¿Cuál es mi nombre?"
    })

    print(resp1["response"])
    print(resp2["response"])
```

### Ejemplo Avanzado: Agente para Servidores

```python
from uruz.core.server_agent import ServerAgent
from uruz.security.vault import Vault
from typing import Dict, Any

class AdminServidor(ServerAgent):
    def __init__(self, agent_id: str, config: dict):
        super().__init__(agent_id, config)
        self.vault = Vault()

    async def ejecutar_comando(self, servidor: str, comando: str) -> Dict[str, Any]:
        # Obtener credenciales del vault
        credenciales = self.vault.get_credential("server_credentials")
        if servidor not in credenciales:
            return {"error": f"No se encontraron credenciales para {servidor}"}

        # Ejecutar comando SSH
        try:
            output, error = await self.execute_ssh_command(servidor, comando)
            return {
                "output": output,
                "error": error,
                "success": not error
            }
        except Exception as e:
            return {"error": str(e)}

    async def process_message(self, message: dict) -> dict:
        # Analizar el mensaje con LLM
        prompt = f"""
        Analiza el siguiente mensaje y extrae:
        1. El servidor objetivo
        2. El comando a ejecutar

        Mensaje: {message['content']}
        """

        analysis = await self.llm.generate(prompt)

        # Ejecutar comando
        if "ejecutar" in message["content"].lower():
            resultado = await self.ejecutar_comando(
                servidor="servidor_principal",
                comando="ls -la"  # Ejemplo
            )

            return {
                "response": f"Resultado de la ejecución: {resultado}",
                "data": resultado
            }

        return {"response": analysis}

# Uso
async def main():
    config = {
        "model": "claude-3-haiku-20240307",
        "temperature": 0.7,
        "max_tokens": 1024,
        "system_prompt": """
        Eres un asistente especializado en administración de servidores.
        Analiza las solicitudes y ejecuta comandos de forma segura.
        """
    }

    agent = AdminServidor("admin_servidor", config)

    # Ejemplo de uso
    response = await agent.process_message({
        "content": "Ejecuta un listado del directorio en el servidor principal"
    })

    print(response["response"])
```

### Ejemplo de Integración con API REST

```python
from fastapi import FastAPI
from uruz.core.llm_agent import LLMAgent
from uruz.api.server import AgentServer

# Crear servidor FastAPI
app = FastAPI()
server = AgentServer()

# Configurar agente
config = {
    "model": "gpt-3.5-turbo-1106",
    "temperature": 0.7,
    "max_tokens": 1024
}
agent = LLMAgent("asistente_api", config)

# Registrar agente
server.add_agent(agent)

# Endpoints personalizados
@app.post("/chat/{agent_id}")
async def chat(agent_id: str, message: str):
    response = await server.process_message(
        agent_id=agent_id,
        message={"content": message}
    )
    return response

# Ejecutar
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Estos ejemplos muestran diferentes niveles de complejidad y casos de uso:

1. **Ejemplo Básico**: Muestra cómo crear y usar un agente simple para responder preguntas.
2. **Ejemplo Intermedio**: Implementa un agente con memoria que mantiene el contexto de la conversación.
3. **Ejemplo Avanzado**: Crea un agente especializado para administración de servidores con acceso seguro mediante vault.
4. **Integración API**: Muestra cómo integrar agentes con una API REST usando FastAPI.

Cada ejemplo puede ser adaptado y extendido según las necesidades específicas del proyecto.

## 🛠️ Uso del CLI

### Comandos Básicos

```bash
# Iniciar el servidor
uruz serve

# Listar agentes activos
uruz list-agents

# Ver estado del sistema
uruz status

# Ver métricas de uso
uruz show-metrics

# Ver historial de comandos
uruz show-history
```

### Gestión de Vault y Caché

```bash
# Crear backup del vault
uruz backup-vault

# Restaurar backup
uruz restore-vault <path_backup>

# Limpiar caché
uruz clear-cache

# Ver estado de colas
uruz show-queues
```

### Mantenimiento

```bash
# Ejecutar tareas de mantenimiento
uruz maintenance --days 30
```

## 🔌 API REST

El servidor expone endpoints en `http://localhost:8000`:

```bash
# Endpoints principales
GET /agents - Lista todos los agentes
POST /agents/{agent_id}/message - Envía mensaje a un agente
GET /metrics - Obtiene métricas del sistema
GET /status - Estado del sistema
```

## 📊 Monitoreo

### Logs

Los logs se almacenan en el directorio `logs/`:

- `app.log`: Logs generales
- `access.log`: Logs de acceso HTTP
- `agent_{id}.log`: Logs específicos de cada agente

### Métricas

Accesibles vía CLI o API:

- Uso de tokens
- Tiempos de respuesta
- Tasa de éxito
- Errores

## 🔒 Seguridad

- Credenciales almacenadas en vault encriptado
- Soporte para claves SSH
- Backups automáticos del vault
- Sanitización de inputs

## 🛠️ Desarrollo

### Estructura del Proyecto

```
uruz/
├── src/
│   └── uruz/
│       ├── api/        # API REST
│       ├── core/       # Lógica central
│       ├── llm/        # Proveedores LLM
│       ├── security/   # Vault y seguridad
│       └── storage/    # Base de datos
├── agents/            # Configuración de agentes
├── scripts/          # Scripts de utilidad
├── tests/           # Tests
└── docs/           # Documentación
```

### Comandos de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements/dev.txt

# Ejecutar tests
pytest

# Construir distribución
python scripts/deploy.py
```

## 🤝 Contribuciones

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -am 'Agrega mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- Documentación: Ver directorio `docs/`
- Issues: Usar el sistema de issues de GitHub
- Contacto: [jm.panozzozenere@gmail.com]

## 🙏 Agradecimientos

- OpenAI por su API GPT
- Anthropic por Claude

---

Hecho con ❤️ usando Python
