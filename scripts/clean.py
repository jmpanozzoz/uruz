#!/usr/bin/env python3
"""Script para limpiar el proyecto antes de la compilación."""

import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ProjectCleaner:
    """Limpia archivos temporales y caché del proyecto."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.paths_to_clean = [
            # Archivos de Python
            "**/*.pyc",
            "**/__pycache__",
            "**/.pytest_cache",
            "**/.coverage",
            "**/.mypy_cache",
            "**/.hypothesis",
            # Archivos de build
            "build/",
            "dist/",
            "*.egg-info",
            # Archivos de datos
            "data/*.db",
            "data/vault.json",
            "data/vault.key",
            "data/backups/",
            # Archivos temporales
            "**/.DS_Store",
            "**/*.log",
            "tmp/",
            # Entorno virtual
            "venv/",
            ".env",
            # Agentes y configuración
            "agents/*.yaml",
            "agents/*.yml",
            "agents/*.json",
            # Redis
            "dump.rdb",
            # Logs
            "logs/*.log",
            "logs/*.log.*",
            # Archivos de estado
            ".uruz_state",
            ".uruz_history",
            # Archivos de caché
            ".cache/",
            # IDE
            ".idea/",
            ".vscode/",
            # Otros
            "**/*.bak",
            "**/*.swp",
            "**/*.swo",
            "**/*~"
        ]
        
    def clean_path(self, path: Path) -> None:
        """Elimina un archivo o directorio."""
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
                logger.info(f"Archivo eliminado: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info(f"Directorio eliminado: {path}")
        except Exception as e:
            logger.error(f"Error eliminando {path}: {e}")
            
    def clean_all(self) -> None:
        """Limpia todos los archivos temporales."""
        logger.info("Iniciando limpieza del proyecto...")
        
        for pattern in self.paths_to_clean:
            for path in self.project_root.glob(pattern):
                self.clean_path(path)
                
        # Limpiar Redis si está corriendo
        try:
            from uruz.cache.redis_provider import RedisProvider
            redis = RedisProvider()
            redis.clear_cache("*")
            logger.info("Caché de Redis limpiado")
        except Exception as e:
            logger.warning(f"No se pudo limpiar Redis: {e}")
                
        logger.info("Limpieza completada")
        
    def create_required_dirs(self) -> None:
        """Crea directorios requeridos vacíos."""
        required_dirs = [
            "data",
            "data/backups",
            "logs",
            "agents",
            "examples",
            "docs"
        ]
        
        for dir_path in required_dirs:
            path = self.project_root / dir_path
            path.mkdir(parents=True, exist_ok=True)
            (path / '.gitkeep').touch()
            logger.info(f"Directorio creado: {path}")
            
    def create_example_files(self) -> None:
        """Crea archivos de ejemplo necesarios."""
        # Crear .env.example si no existe
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            env_content = """# Configuración de Base de Datos
DATABASE_URL=sqlite:///./uruz.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
DEFAULT_LLM_PROVIDER=default-provider
OPENAI_API_KEY=tu-api-key-aquí
ANTHROPIC_API_KEY=tu-api-key-aquí

# SSH
SSH_KEY_PATH=your-ssh-key-path-here"""
            env_example.write_text(env_content)
            logger.info("Archivo .env.example creado")

def main():
    """Función principal."""
    try:
        cleaner = ProjectCleaner()
        cleaner.clean_all()
        cleaner.create_required_dirs()
        cleaner.create_example_files()
        logger.info("Proyecto limpio y listo para compilación")
    except Exception as e:
        logger.error(f"Error durante la limpieza: {e}")
        raise

if __name__ == '__main__':
    main() 