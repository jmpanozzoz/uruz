#!/bin/bash

echo "🚀 Iniciando Uruz Framework en Linux..."

# Activar/crear entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

# Verificar/Instalar Redis
echo "🔍 Verificando Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo "⚙️  Instalando Redis..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install redis-server -y
    elif command -v yum &> /dev/null; then
        sudo yum install redis -y
    else
        echo "⚠️  No se pudo instalar Redis automáticamente"
        exit 1
    fi
fi

# Iniciar Redis
if ! systemctl is-active --quiet redis; then
    echo "🔄 Iniciando Redis..."
    sudo systemctl start redis
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