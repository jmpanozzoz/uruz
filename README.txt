URUZ FRAMEWORK
=============

Un framework moderno y extensible para la creación de sistemas multiagente con IA.

CARACTERÍSTICAS PRINCIPALES
-------------------------

* Arquitectura Multiagente
  - Sistema robusto para la creación y gestión de múltiples agentes interactivos
  - Comunicación entre agentes
  - Sistema de estados y acciones

* Integración con LLMs
  - Soporte nativo para OpenAI
  - Soporte para Anthropic
  - Extensible para otros proveedores

* Seguridad
  - Sistema de vault para credenciales
  - Encriptación automática
  - Gestión segura de API keys
  - Backup y restauración de credenciales

* API y Caché
  - API REST basada en FastAPI
  - Caché Redis con gestión avanzada
  - Sistema de colas para tareas
  - Métricas y monitoreo

INSTALACIÓN
-----------

Instalación básica:
    pip install uruz-framework

Instalación para desarrollo:
    git clone https://github.com/tuusuario/uruz-framework.git
    cd uruz-framework
    pip install -e ".[dev]"

INICIO RÁPIDO
------------

1. Configuración:
   Crear archivo .env:
   
   DATABASE_URL=sqlite:///./uruz.db
   REDIS_HOST=localhost
   REDIS_PORT=6379
   OPENAI_API_KEY=tu-api-key-aquí
   ANTHROPIC_API_KEY=tu-api-key-aquí

2. Comandos CLI:

   Iniciar servidor:
       uruz serve

   Ver estado:
       uruz status

   Gestionar agentes:
       uruz list-agents
       uruz show-metrics
       uruz show-history

   Gestionar vault:
       uruz backup-vault
       uruz restore-vault <path>

   Gestionar caché:
       uruz clear-cache
       uruz show-queues

   Ver documentación completa:
       docs/cli.txt

3. Uso programático:

   from uruz.core.agent import Agent
   from uruz.security.vault import Vault
   from uruz.llm.openai_provider import OpenAIProvider

   # Configurar vault
   vault = Vault()
   vault.store_credential("openai_api_key", "tu-api-key")

   # Crear agente
   class MyAgent(Agent):
       async def process_message(self, message):
           response = await self.llm.generate(message["content"])
           return {"response": response}
       
       async def act(self):
           return [{"status": "active"}]

   # Usar agente
   agent = MyAgent("agent-1", config={})

ESTRUCTURA DEL PROYECTO
---------------------

src/uruz/
    core/           - Componentes principales
    llm/            - Integraciones con LLMs
    cache/          - Sistemas de caché
    storage/        - Almacenamiento
    api/            - Servidor API
    security/       - Gestión de seguridad
    utils/          - Utilidades y logging

tests/             - Tests unitarios y de integración
docs/              - Documentación detallada
    cli.txt        - Referencia completa de comandos
    api.txt        - Documentación de la API
    config.txt     - Guía de configuración
examples/          - Ejemplos de uso
scripts/           - Scripts de utilidad

DESARROLLO
---------

1. Instalar dependencias:
   pip install -e ".[dev,test]"

2. Ejecutar tests:
   pytest
   pytest --cov=uruz

3. Verificar estilo:
   black src/
   flake8 src/

DEPENDENCIAS
-----------

Base:
- fastapi>=0.68.0
- uvicorn>=0.15.0
- pydantic>=1.8.2
- cryptography>=3.4.7
- redis>=4.0.0
- sqlalchemy>=1.4.23
- openai>=0.27.0
- anthropic>=0.3.0
- click>=8.0.0
- paramiko>=3.4.0

Desarrollo:
- black>=22.3.0
- isort>=5.10.1
- flake8>=4.0.1
- mypy>=0.950

Testing:
- pytest>=7.1.2
- pytest-asyncio>=0.18.3
- pytest-cov>=3.0.0

DOCUMENTACIÓN
------------

Consultar la carpeta docs/ para:
- Guía de inicio (getting_started.txt)
- Configuración (configuration.txt)
- Referencia API (api_reference.txt)

CONTRIBUIR
---------

1. Fork el repositorio
2. Crear rama feature (git checkout -b feature/NuevaCaracteristica)
3. Commit cambios (git commit -m 'Agregar característica')
4. Push a la rama (git push origin feature/NuevaCaracteristica)
5. Crear Pull Request

LICENCIA
--------

MIT License - Ver archivo LICENSE

CONTACTO
--------

Autor: Tu Nombre
Email: email@ejemplo.com
GitHub: https://github.com/tuusuario/uruz-framework
