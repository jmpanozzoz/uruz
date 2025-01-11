"""Script para inicializar el entorno de Uruz"""
import os
import sys
from pathlib import Path

def setup_environment():
    # Crear directorios necesarios
    directories = [
        'agents',
        'logs',
        'data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Verificar .env
    if not os.path.exists('.env'):
        print("Creando archivo .env...")
        with open('.env.example', 'r') as source:
            with open('.env', 'w') as target:
                target.write(source.read())
        print("Por favor, edita el archivo .env con tus credenciales")
    
    # Verificar base de datos
    if not os.path.exists('data/uruz.db'):
        print("Inicializando base de datos...")
        from uruz.storage.database import SQLAlchemyProvider
        db = SQLAlchemyProvider("sqlite:///./data/uruz.db")
        db.connect()
        # Aquí podrías agregar la creación de tablas si es necesario
    
    print("Configuración completada!")

if __name__ == "__main__":
    setup_environment() 