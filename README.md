# Uruz Framework

Un framework moderno y extensible para la creación de sistemas multiagente con IA.

## Características

- Arquitectura Multiagente: Sistema robusto para la creación y gestión de múltiples agentes interactivos
- Integración con LLMs: Soporte nativo para OpenAI, Anthropic y otros proveedores
- Seguridad Integrada: Sistema de vault para gestión segura de credenciales
- API REST: Interfaz HTTP moderna basada en FastAPI
- Caché Configurable: Soporte para diferentes sistemas de caché (Redis, Memoria)
- Almacenamiento Flexible: Integración con múltiples bases de datos

## Instalación

Instalación básica:
pip install uruz-framework

Instalación para desarrollo:
git clone https://github.com/tuusuario/uruz-framework.git
cd uruz-framework
pip install -e ".[dev]"

## Uso Básico

Ejemplo de creación de un agente:

from uruz.core.agent import Agent
from uruz.security.vault import Vault
from uruz.llm.openai_provider import OpenAIProvider

# Configurar credenciales

vault = Vault()
vault.store_credential("openai_api_key", "tu-api-key-aquí")

# Configurar proveedor LLM

llm_config = {
"api_key": vault.get_credential("openai_api_key"),
"model": "gpt-4"
}
llm = OpenAIProvider(llm_config)

# Crear y usar un agente

class MyAgent(Agent):
async def process_message(self, message):
response = await self.llm.generate(message["content"])
return {"response": response}

    async def act(self):
        # Implementa la lógica de acción del agente
        pass

# Uso

agent = MyAgent("agent-1", config={})
response = await agent.process_message({"content": "¿Cuál es el siguiente paso?"})

Ejemplo de uso de la API REST:

from uruz.api.server import AgentServer

# Crear servidor

server = AgentServer()

# Registrar agentes

server.agents["agent-1"] = MyAgent("agent-1", config={})

# Ejecutar servidor

import uvicorn
uvicorn.run(server.app, host="0.0.0.0", port=8000)

## Desarrollo

Estructura del Proyecto:
uruz-framework/
├── src/uruz/ # Código fuente principal
├── tests/ # Tests unitarios y de integración
├── docs/ # Documentación
└── examples/ # Ejemplos de uso

Ejecutar Tests:

# Instalar dependencias de desarrollo

pip install -e ".[dev,test]"

# Ejecutar tests

pytest

# Con cobertura

pytest --cov=uruz

## Documentación

La documentación detallada está disponible en la carpeta docs/:

- Guía de Inicio (docs/getting_started.md)
- Configuración (docs/configuration.md)
- API Reference (docs/api_reference.md)

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
3. Commit tus cambios (git commit -m 'Add some AmazingFeature')
4. Push a la rama (git push origin feature/AmazingFeature)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## Agradecimientos

- OpenAI por su API de GPT
- FastAPI por el excelente framework web
- La comunidad de Python por todas las herramientas utilizadas

## Contacto

Tu Nombre - @tutwitter - email@ejemplo.com
Link del Proyecto: https://github.com/tuusuario/uruz-framework
