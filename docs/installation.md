# 📥 Instalación de Uruz Framework

## Requisitos del Sistema

### Python
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Base de Datos
- SQLite 3 (incluido con Python)

### Cache (Opcional)
- Redis 6.0 o superior

## Instalación del Framework

### Desde PyPI
```bash
pip install uruz-framework
```

### Modo Desarrollo
```bash
git clone https://github.com/tu-usuario/uruz.git
cd uruz
pip install -e .
```

## Configuración Inicial

### 1. Inicializar Proyecto
```bash
# Crear nuevo proyecto
uruz init --name mi_proyecto

# Entrar al directorio del proyecto
cd mi_proyecto
```

### 2. Configurar Credenciales
```bash
# Configurar credenciales del sistema
uruz setup-credentials

# Verificar credenciales almacenadas
uruz list-credentials
```

### 3. Verificar Instalación
```bash
# Verificar estado del sistema
uruz check-system
```

### 4. Iniciar Servicios
```bash
# Iniciar servicios del sistema
uruz start

# O iniciar solo el servidor API
uruz serve
```

## Estructura del Proyecto
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
└── .env.example      # Ejemplo de variables de entorno
```

## Mantenimiento

### Limpieza del Sistema
```bash
# Ver categorías disponibles
uruz clean list-categories

# Limpiar todo
uruz clean all

# Limpiar una categoría específica
uruz clean category cache
```

### Tareas de Mantenimiento
```bash
# Ejecutar todas las tareas
uruz maintenance run-all

# Limpiar logs antiguos
uruz maintenance cleanup-logs --days 30

# Optimizar base de datos
uruz maintenance optimize-db
```

### Gestión de Credenciales
```bash
# Crear backup del vault
uruz backup-vault

# Restaurar vault desde backup
uruz restore-vault --file backup.json

# Limpiar caché
uruz clear-cache
```

## Solución de Problemas

### Redis no inicia
1. Verificar que Redis está instalado:
   ```bash
   redis-cli ping
   ```
2. Iniciar Redis manualmente:
   - macOS: `brew services start redis`
   - Linux: `sudo systemctl start redis`
   - Windows: Iniciar desde Servicios

### Errores de Permisos
1. Verificar permisos de directorios:
   ```bash
   ls -la data/
   ```
2. Ajustar permisos si es necesario:
   ```bash
   chmod -R 755 data/
   ```

### Base de Datos
1. Verificar conexión:
   ```bash
   uruz status
   ```
2. Optimizar si hay problemas de rendimiento:
   ```bash
   uruz maintenance optimize-db
   ```

## Actualización

### Actualizar Framework
```bash
pip install --upgrade uruz-framework
```

### Limpiar Caché después de Actualizar
```bash
uruz clear-cache
uruz clean category cache
``` 