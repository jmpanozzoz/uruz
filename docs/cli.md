# 🖥️ CLI de Uruz

Este documento describe todos los comandos disponibles en la interfaz de línea de comandos (CLI) de Uruz.

## 🚀 Comandos Principales

### 1. Iniciar Servidor
```bash
uruz serve [opciones]
```
**Opciones:**
- `--host`: Host para el servidor (default: configuración)
- `--port`: Puerto para el servidor (default: configuración)
- `--debug`: Activa modo debug

**Ejemplos:**
```bash
uruz serve
uruz serve --debug --port 8080
```

### 2. Listar Agentes
```bash
uruz list-agents
```
Muestra los agentes activos en el sistema.

### 3. Estado del Sistema
```bash
uruz status [opciones]
```
**Opciones:**
- `--check-deps`: Verifica las dependencias instaladas

**Ejemplos:**
```bash
uruz status
uruz status --check-deps
```

### 4. Métricas de Uso
```bash
uruz show-metrics
```
Muestra estadísticas detalladas:
- Tiempo de procesamiento
- Tokens utilizados
- Tasa de éxito
- Errores encontrados

### 5. Historial de Comandos
```bash
uruz show-history [opciones]
```
**Opciones:**
- `--server`: Filtrar por servidor específico
- `--limit`: Número máximo de registros (default: 10)

**Ejemplos:**
```bash
uruz show-history
uruz show-history --server groovinads --limit 20
```

## 🛠️ Comandos de Mantenimiento

### 6. Mantenimiento del Sistema
```bash
uruz maintenance [opciones]
```
**Opciones:**
- `--days`: Días de antigüedad para limpieza (default: 30)

**Ejemplos:**
```bash
uruz maintenance
uruz maintenance --days 60
```

### 7. Backup del Vault
```bash
uruz backup-vault
```
Crea una copia de seguridad en `data/backups/vault_YYYYMMDD_HHMMSS/`

### 8. Restaurar Vault
```bash
uruz restore-vault <backup_path>
```
**Ejemplo:**
```bash
uruz restore-vault data/backups/vault_20240111_120000/
```

### 9. Limpiar Caché
```bash
uruz clear-cache [opciones]
```
**Opciones:**
- `--pattern`: Patrón para limpiar caché específico (default: *)

**Ejemplos:**
```bash
uruz clear-cache
uruz clear-cache --pattern "llm:response:*"
```

### 10. Estado de Colas
```bash
uruz show-queues
```
Muestra información sobre:
- Cola de tareas
- Cola de eventos
- Número de elementos en cada cola

## ℹ️ Características Generales

- Todos los comandos incluyen manejo de errores
- Logging detallado de operaciones
- Salida formateada para mejor legibilidad
- Opciones de configuración flexibles
- Integración con sistema de métricas

> Para más información sobre cada comando, puede usar:
> ```bash
> uruz [comando] --help
> ``` 