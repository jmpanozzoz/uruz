"""
Módulo para limpiar el proyecto y gestionar archivos temporales.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.logging import logger
from ..cache.redis_provider import RedisProvider

class ProjectCleaner:
    """Gestor de limpieza del proyecto."""
    
    # Patrones de archivos a limpiar por categoría
    CLEANUP_PATTERNS = {
        "python": [
            "**/*.pyc",
            "**/__pycache__",
            "**/.pytest_cache",
            "**/.coverage",
            "**/.mypy_cache",
            "**/.hypothesis",
        ],
        "build": [
            "build/",
            "dist/",
            "*.egg-info",
        ],
        "data": [
            "data/*.db",
            "data/vault.json",
            "data/vault.key",
            "data/backups/",
        ],
        "temp": [
            "**/.DS_Store",
            "**/*.log",
            "tmp/",
        ],
        "env": [
            "venv/",
            ".env",
        ],
        "agents": [
            "agents/*.yaml",
            "agents/*.yml",
            "agents/*.json",
        ],
        "redis": [
            "dump.rdb",
        ],
        "logs": [
            "logs/*.log",
            "logs/*.log.*",
        ],
        "state": [
            ".uruz_state",
            ".uruz_history",
        ],
        "cache": [
            ".cache/",
        ],
        "ide": [
            ".idea/",
            ".vscode/",
        ],
        "backup": [
            "**/*.bak",
            "**/*.swp",
            "**/*.swo",
            "**/*~",
        ]
    }
    
    # Directorios requeridos por el proyecto
    REQUIRED_DIRS = [
        "data",
        "data/backups",
        "data/logs",
        "data/storage",
        "data/vault",
        "logs",
        "agents",
        "examples",
        "docs"
    ]
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Inicializa el gestor de limpieza.
        
        Args:
            project_root: Ruta raíz del proyecto. Si no se especifica, usa el directorio actual.
        """
        self.project_root = project_root or Path.cwd()
        self.redis = RedisProvider()
    
    def clean_path(self, path: Path) -> bool:
        """
        Elimina un archivo o directorio.
        
        Args:
            path: Ruta a eliminar.
            
        Returns:
            bool: True si la eliminación fue exitosa.
        """
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
                logger.info(f"✓ Archivo eliminado: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info(f"✓ Directorio eliminado: {path}")
            return True
        except Exception as e:
            logger.error(f"⚠️  Error eliminando {path}: {e}")
            return False
    
    def clean_by_patterns(self, patterns: List[str]) -> int:
        """
        Limpia archivos que coinciden con los patrones especificados.
        
        Args:
            patterns: Lista de patrones glob a limpiar.
            
        Returns:
            int: Número de archivos eliminados.
        """
        cleaned = 0
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                if self.clean_path(path):
                    cleaned += 1
        return cleaned
    
    def clean_by_category(self, category: str) -> int:
        """
        Limpia archivos de una categoría específica.
        
        Args:
            category: Categoría de archivos a limpiar.
            
        Returns:
            int: Número de archivos eliminados.
        """
        if category not in self.CLEANUP_PATTERNS:
            logger.error(f"⚠️  Categoría desconocida: {category}")
            return 0
            
        logger.info(f"🧹 Limpiando archivos de {category}...")
        return self.clean_by_patterns(self.CLEANUP_PATTERNS[category])
    
    def clean_all(self, categories: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Limpia todos los archivos temporales.
        
        Args:
            categories: Lista de categorías a limpiar. Si es None, limpia todas.
            
        Returns:
            Dict[str, int]: Número de archivos eliminados por categoría.
        """
        results = {}
        categories = categories or list(self.CLEANUP_PATTERNS.keys())
        
        logger.info("🧹 Iniciando limpieza del proyecto...")
        
        for category in categories:
            results[category] = self.clean_by_category(category)
            
        # Limpiar Redis si está configurado
        try:
            self.redis.clear_cache("*")
            logger.info("✓ Caché de Redis limpiado")
            results["redis_cache"] = 1
        except Exception as e:
            logger.warning(f"⚠️  No se pudo limpiar Redis: {e}")
            results["redis_cache"] = 0
            
        logger.info("✨ Limpieza completada")
        return results
    
    def create_required_dirs(self) -> List[Path]:
        """
        Crea directorios requeridos vacíos.
        
        Returns:
            List[Path]: Lista de directorios creados.
        """
        created_dirs = []
        logger.info("📁 Creando directorios requeridos...")
        
        for dir_path in self.REQUIRED_DIRS:
            path = self.project_root / dir_path
            try:
                path.mkdir(parents=True, exist_ok=True)
                gitkeep = path / '.gitkeep'
                if not gitkeep.exists():
                    gitkeep.touch()
                created_dirs.append(path)
                logger.info(f"✓ Directorio creado: {path}")
            except Exception as e:
                logger.error(f"⚠️  Error creando directorio {path}: {e}")
                
        return created_dirs
    
    def create_example_files(self) -> List[Path]:
        """
        Crea archivos de ejemplo necesarios.
        
        Returns:
            List[Path]: Lista de archivos creados.
        """
        created_files = []
        logger.info("📝 Creando archivos de ejemplo...")
        
        # Crear .env.example si no existe
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            try:
                env_content = """# Configuración del Proyecto
URUZ_ENV=development
URUZ_PROJECT_NAME=mi_proyecto

# Directorios del Proyecto
URUZ_AGENTS_DIR=agents
URUZ_DATA_DIR=data
URUZ_CONFIG_DIR=config

# Base de Datos
DATABASE_URL=sqlite:///data/storage/uruz.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
DEFAULT_LLM_PROVIDER=anthropic
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Seguridad
SSH_KEY_PATH=~/.ssh/id_rsa

# API Server
API_HOST=0.0.0.0
API_PORT=8000"""
                env_example.write_text(env_content)
                created_files.append(env_example)
                logger.info(f"✓ Archivo creado: {env_example}")
            except Exception as e:
                logger.error(f"⚠️  Error creando {env_example}: {e}")
                
        return created_files
    
    def setup_project(self) -> bool:
        """
        Configura el proyecto limpio y listo para usar.
        
        Returns:
            bool: True si la configuración fue exitosa.
        """
        try:
            # Limpiar proyecto
            results = self.clean_all()
            total_cleaned = sum(results.values())
            logger.info(f"✓ {total_cleaned} archivos limpiados")
            
            # Crear estructura
            dirs = self.create_required_dirs()
            logger.info(f"✓ {len(dirs)} directorios creados")
            
            # Crear archivos de ejemplo
            files = self.create_example_files()
            logger.info(f"✓ {len(files)} archivos de ejemplo creados")
            
            logger.info("✨ Proyecto configurado correctamente")
            return True
        except Exception as e:
            logger.error(f"⚠️  Error configurando proyecto: {e}")
            return False 