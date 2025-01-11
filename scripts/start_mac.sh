#!/bin/bash

echo "🚀 Iniciando Uruz Framework en macOS..."

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

# Instalar el framework en modo desarrollo
echo "📦 Instalando Uruz Framework..."
pip install -e ".[dev,test]"

# Verificar/Instalar dependencias
echo "🔍 Verificando Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo "⚙️  Instalando Redis..."
    brew install redis
fi

# Iniciar Redis
if ! brew services list | grep -q "redis.*started"; then
    echo "🔄 Iniciando Redis..."
    brew services start redis
fi

# Verificar instalación
if [ ! -f ".env" ]; then
    echo "⚙️  Configurando entorno..."
    python scripts/setup.py
fi

# Verificar sistema
echo "🔍 Verificando sistema..."
python scripts/check_system.py

# Iniciar servidor
if [ $? -eq 0 ]; then
    echo "🚀 Iniciando servidor Uruz..."
    uruz serve
fi 