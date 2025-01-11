@echo off
echo 🚀 Iniciando Uruz Framework en Windows...

:: Verificar entorno virtual
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Verificar Redis (asumiendo instalación con Windows Subsystem for Linux)
echo 🔍 Verificando Redis...
wsl redis-cli ping > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis no encontrado. Por favor, instala Redis usando WSL
    echo Instrucciones:
    echo 1. Instala WSL: wsl --install
    echo 2. En WSL, ejecuta: sudo apt-get install redis-server
    echo 3. Inicia Redis: sudo service redis-server start
    exit /b 1
)

:: Verificar instalación
if not exist ".env" (
    echo ⚙️  Configurando entorno...
    python scripts\setup.py
)

:: Verificar sistema
echo 🔍 Verificando sistema...
python scripts\check_system.py

:: Iniciar servidor
if errorlevel 0 (
    echo 🚀 Iniciando servidor Uruz...
    uruz serve
) 