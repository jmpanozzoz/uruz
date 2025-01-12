# 🖥️ CLI de Uruz

Este documento describe todos los comandos disponibles en la interfaz de línea de comandos (CLI) de Uruz.

## 🚀️ Comandos de Uruz Framework

### Inicialización y Configuración

#### `uruz init [opciones]`
Inicializa un nuevo proyecto.
- `--name TEXT`: Nombre del proyecto
- `--path TEXT`: Ruta donde crear el proyecto (opcional)
- `--api`: Incluir configuración de API server
- `--redis`: Incluir configuración de Redis

#### `uruz setup-credentials`
Configura las credenciales del sistema de forma interactiva.
- Tipos de credenciales soportados:
  - llm: API keys para OpenAI y Anthropic
  - database: Credenciales de base de datos
  - ssh: Claves SSH
  - custom: Credenciales personalizadas

#### `uruz list-credentials`
Lista las credenciales almacenadas en el vault.

#### `uruz check-system`
Verifica el estado del sistema y sus dependencias.

#### `uruz start [opciones]`
Inicia los servicios del sistema.
- `--force`: Forzar inicio incluso si hay errores

### Servidor y Agentes

#### `uruz serve [opciones]`
Inicia el servidor API.
- `--host TEXT`: Host para el servidor (default: 0.0.0.0)
- `--port INTEGER`: Puerto para el servidor (default: 8000)
- `--debug`: Modo debug

#### `uruz create-agent [opciones]`
Crea un nuevo agente.
- `--name TEXT`: Nombre del agente [requerido]
- `--type TEXT`: Tipo de agente (llm/server/simple) [requerido]

#### `uruz list-agents`
Lista todos los agentes disponibles.

#### `uruz status [opciones]`
Muestra el estado del sistema.
- `--check-deps`: Verificar dependencias

#### `uruz show-metrics`
Muestra métricas de uso de los agentes.

#### `uruz show-history [opciones]`
Muestra el historial de comandos.
- `--server TEXT`: Filtrar por servidor
- `--limit INTEGER`: Número máximo de registros (default: 10)

#### `uruz show-queues`
Muestra el estado de las colas de mensajes.

### Mantenimiento

#### `uruz maintenance cleanup-logs [opciones]`
Limpia logs antiguos.
- `--days INTEGER`: Días de antigüedad (default: 30)

#### `uruz maintenance cleanup-metrics [opciones]`
Limpia métricas antiguas.
- `--days INTEGER`: Días de antigüedad (default: 90)

#### `uruz maintenance cleanup-backups [opciones]`
Mantiene solo los backups más recientes.
- `--keep INTEGER`: Número de backups a mantener (default: 10)

#### `uruz maintenance optimize-db`
Optimiza la base de datos.

#### `uruz maintenance run-all [opciones]`
Ejecuta todas las tareas de mantenimiento.
- `--log-days INTEGER`: Días para retener logs (default: 30)
- `--metric-days INTEGER`: Días para retener métricas (default: 90)
- `--backups-keep INTEGER`: Backups a mantener (default: 10)

### Limpieza

#### `uruz clean all [opciones]`
Limpia todos los archivos temporales.
- `-c, --category TEXT`: Categorías específicas a limpiar

#### `uruz clean category [opciones]`
Limpia una categoría específica.
- `--name TEXT`: Nombre de la categoría [requerido]

#### `uruz clean list-categories`
Lista las categorías disponibles para limpieza.

#### `uruz clean setup`
Configura un proyecto limpio.

### Vault y Caché

#### `uruz backup-vault`
Crea un backup del vault.

#### `uruz restore-vault [opciones]`
Restaura el vault desde un backup.
- `--file TEXT`: Archivo de backup [requerido]

#### `uruz clear-cache`
Limpia la caché del sistema.

### Despliegue

#### `uruz deploy check-deps [opciones]`
Verifica dependencias de despliegue.
- `--auto-install`: Instalar dependencias faltantes

#### `uruz deploy check-git [opciones]`
Verifica configuración de Git.
- `--auto-init`: Inicializar repositorio si no existe

#### `uruz deploy check-reqs [opciones]`
Verifica archivos de requirements.
- `--auto-create`: Crear archivos si no existen

#### `uruz deploy build`
Construye el proyecto para distribución.

#### `uruz deploy pypi`
Despliega el proyecto a PyPI.

## ℹ️ Características Generales

- Todos los comandos incluyen manejo de errores
- Logging detallado de operaciones
- Salida formateada para mejor legibilidad
- Opciones de configuración flexibles
- Integración con sistema de métricas

> Para más información sobre cada comando:
> ```bash
> uruz [comando] --help
> ``` 