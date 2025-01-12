# 🚀 Uruz Framework

Framework de desarrollo para crear y gestionar agentes de IA de forma segura y eficiente.

## ✨ Características

- 🤖 **Múltiples Proveedores de IA**: Soporte para OpenAI, Anthropic y más
- 🔐 **Gestión Segura de Credenciales**: Sistema de vault encriptado sincronizado con .env
- 🛠️ **CLI Potente**: Comandos para todas las operaciones comunes
- 🌐 **API REST**: Endpoints para interactuar con agentes
- 💾 **Caché con Redis**: Optimización de respuestas y gestión de colas
- 📊 **Métricas en SQLite**: Almacenamiento de métricas e historial
- 📝 **Logging Detallado**: Sistema de logs para monitoreo y debugging
- 🔄 **Despliegue Automatizado**: Herramientas para publicar en PyPI
- 🧹 **Sistema de Mantenimiento**: Limpieza y optimización integrada

## 🔧 Requisitos

- Python 3.8+
- pip (gestor de paquetes)
- Redis 6.0+ (opcional)
- SQLite 3 (incluido con Python)

## 📦 Instalación

```bash
# Instalar desde PyPI
pip install uruz-framework

# Inicializar proyecto
uruz init --name mi_proyecto
cd mi_proyecto

# Configurar credenciales
uruz setup-credentials

# Verificar instalación
uruz check-system
```

## 🚀 Inicio Rápido

### 1. Configurar Credenciales
```bash
# Configurar nuevas credenciales
uruz setup-credentials

# Ver credenciales almacenadas
uruz list-credentials
```

### 2. Crear un Agente
```bash
# Crear agente desde CLI
uruz create-agent --name mi_agente --type llm

# O manualmente en agents/mi_agente.yaml:
```
```yaml
name: mi_agente
type: llm
provider: openai
model: gpt-4
max_tokens: 2000
temperature: 0.7
system_prompt: |
  Eres un asistente experto en Python.
```

### 3. Iniciar el Servidor
```bash
# Iniciar en modo debug
uruz serve --debug

# O iniciar todos los servicios
uruz start
```

## 🛠️ Comandos Principales

### Inicialización
```bash
uruz init --name proyecto     # Crear proyecto
uruz setup-credentials        # Configurar credenciales
uruz check-system            # Verificar instalación
uruz start                   # Iniciar servicios
```

### Agentes
```bash
uruz create-agent            # Crear agente
uruz list-agents            # Listar agentes
uruz status                 # Ver estado
```

### Mantenimiento
```bash
uruz maintenance run-all    # Ejecutar mantenimiento
uruz clean all             # Limpiar sistema
uruz backup-vault          # Respaldar credenciales
```

### Monitoreo
```bash
uruz show-metrics          # Ver métricas
uruz show-history         # Ver historial
uruz show-queues         # Estado de colas
```

## 📁 Estructura del Proyecto

```
mi_proyecto/
├── agents/               # Configuraciones de agentes
│   └── example_agent.yaml
├── api/                 # Código del servidor API
│   └── main.py
├── config/             # Configuraciones
│   └── environments/
│       ├── development.yaml
│       └── production.yaml
├── data/               # Datos y almacenamiento
│   ├── backups/
│   ├── logs/
│   └── storage/
├── .env               # Variables de entorno
└── .env.example      # Ejemplo de variables
```

## 📚 Documentación

- [Guía de Instalación](docs/installation.md)
- [Referencia de CLI](docs/cli.md)
- [Ejemplos](examples/)

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
