# 📥 Guía de Instalación de Uruz Framework

Esta guía explica cómo instalar y configurar Uruz Framework en diferentes sistemas operativos.

## 📋 Requisitos Previos

### General
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Por Sistema Operativo

#### macOS
- Homebrew
- Command Line Tools

#### Windows
- Windows Subsystem for Linux (WSL)
- Visual Studio Build Tools

#### Linux
- build-essential
- python3-dev

## 🚀 Instalación por Sistema Operativo

### 1. macOS

```bash
# Instalar Homebrew (si no está instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Clonar repositorio
git clone https://github.com/tuusuario/uruz-framework.git
cd uruz-framework

# Ejecutar script de inicio
chmod +x scripts/start_mac.sh
./scripts/start_mac.sh
```

### 2. Windows

```bash
# Instalar WSL (si no está instalado)
wsl --install

# Clonar repositorio
git clone https://github.com/tuusuario/uruz-framework.git
cd uruz-framework

# Ejecutar script de inicio
scripts\start_windows.bat
```

### 3. Linux

```bash
# Instalar dependencias
sudo apt update && sudo apt install python3-dev build-essential

# Clonar repositorio
git clone https://github.com/tuusuario/uruz-framework.git
cd uruz-framework

# Ejecutar script de inicio
chmod +x scripts/start_linux.sh
./scripts/start_linux.sh
```

## ✅ Verificación de la Instalación

Para verificar que todo está funcionando:

1. El script de inicio debería mostrar ✓ en todas las verificaciones
2. Probar crear un agente:
   ```bash
   uruz create-agent --name "test" --type simple
   ```
3. Ejecutar el test del sistema:
   ```bash
   python examples/test_system.py
   ```

## 🔧 Solución de Problemas

### 1. Redis no inicia
- **macOS**: `brew services restart redis`
- **Windows**: Reiniciar WSL
- **Linux**: `sudo systemctl restart redis`

### 2. Error de permisos
- **macOS/Linux**: `sudo chown -R $USER:$USER .`
- **Windows**: Ejecutar como administrador

### 3. Error de conexión a la API
- Verificar `.env`
- Comprobar que el puerto no está en uso

## 🛠️ Mantenimiento

### 1. Actualizar el framework
```bash
pip install -e ".[dev]" --upgrade
```

### 2. Limpiar caché
```bash
redis-cli flushall
```

### 3. Reiniciar servicios
```bash
./scripts/start_{os}.sh
```

> Para más información, consultar la documentación en `docs/` 