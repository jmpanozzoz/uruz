"""
Módulo para verificación del sistema.
"""
import sys
import platform
import pkg_resources
import redis
from typing import List, Optional
from ..config import settings

def check_system() -> List[str]:
    """
    Verifica el estado del sistema y sus dependencias.
    
    Returns:
        List[str]: Lista de problemas encontrados. Lista vacía si todo está bien.
    """
    issues = []
    
    # Verificar versión de Python
    python_version = sys.version_info
    if python_version < (3, 8):
        issues.append(f"Python {python_version.major}.{python_version.minor} no es compatible. Se requiere Python 3.8+")
    
    # Verificar dependencias
    required_packages = {
        'fastapi': '0.100.0',
        'uvicorn': '0.22.0',
        'redis': '4.5.0',
        'pydantic': '2.0.0',
        'anthropic': '0.3.0',
        'openai': '1.0.0'
    }
    
    for package, min_version in required_packages.items():
        try:
            installed = pkg_resources.get_distribution(package)
            if pkg_resources.parse_version(installed.version) < pkg_resources.parse_version(min_version):
                issues.append(f"{package} {installed.version} es anterior a la versión mínima requerida {min_version}")
        except pkg_resources.DistributionNotFound:
            issues.append(f"No se encontró el paquete {package}")
    
    # Verificar Redis si está configurado
    if settings.REDIS_HOST and settings.REDIS_PORT:
        try:
            r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                socket_connect_timeout=1
            )
            r.ping()
        except redis.ConnectionError:
            issues.append(f"No se pudo conectar a Redis en {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
    # Verificar archivo .env
    try:
        with open(".env") as f:
            env_content = f.read()
            if "your-key-here" in env_content:
                issues.append("El archivo .env contiene valores por defecto que deben ser configurados")
    except FileNotFoundError:
        issues.append("No se encontró el archivo .env")
    
    # Verificar directorios necesarios
    required_dirs = [
        settings.URUZ_AGENTS_DIR,
        settings.URUZ_DATA_DIR,
        settings.URUZ_CONFIG_DIR
    ]
    
    for dir_path in required_dirs:
        if not dir_path or not dir_path.strip():
            issues.append(f"La ruta del directorio {dir_path} no está configurada")
    
    return issues 