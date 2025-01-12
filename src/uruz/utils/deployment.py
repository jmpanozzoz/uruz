"""
Módulo para gestionar el despliegue del proyecto a PyPI.
"""
import os
import sys
import subprocess
import configparser
import re
from pathlib import Path
from typing import Optional, Tuple, Dict
from importlib.metadata import version, PackageNotFoundError
from ..utils.logging import logger

class DeploymentManager:
    """Gestor de despliegue del proyecto."""
    
    REQUIRED_PACKAGES = {
        'build': 'build>=0.10.0',
        'twine': 'twine>=4.0.2',
        'setuptools': 'setuptools>=68.0.0',
        'wheel': 'wheel>=0.40.0',
        'setuptools_scm': 'setuptools_scm>=8.0.0'
    }
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Inicializa el gestor de despliegue.
        
        Args:
            project_root: Ruta raíz del proyecto. Si no se especifica, usa el directorio actual.
        """
        self.project_root = project_root or Path.cwd()
        self.version_file = self.project_root / "src" / "uruz" / "__init__.py"
        self.pyproject_file = self.project_root / "pyproject.toml"
    
    def check_dependencies(self, auto_install: bool = False) -> Dict[str, bool]:
        """
        Verifica que las dependencias necesarias estén instaladas.
        
        Args:
            auto_install: Si es True, instala automáticamente las dependencias faltantes.
            
        Returns:
            Dict[str, bool]: Estado de cada dependencia.
        """
        status = {}
        missing_packages = []
        
        for package, requirement in self.REQUIRED_PACKAGES.items():
            try:
                current_version = version(package)
                logger.info(f"✓ {package} versión {current_version}")
                status[package] = True
            except PackageNotFoundError:
                missing_packages.append(requirement)
                status[package] = False
                
        if missing_packages and auto_install:
            try:
                for package in missing_packages:
                    logger.info(f"📦 Instalando {package}...")
                    subprocess.run([
                        sys.executable, "-m", "pip", "install",
                        package
                    ], check=True)
                    status[package.split('>=')[0]] = True
                logger.info("✨ Dependencias instaladas correctamente")
            except subprocess.CalledProcessError as e:
                logger.error(f"⚠️  Error instalando dependencias: {e}")
        
        return status

    def check_git_setup(self, auto_init: bool = False) -> bool:
        """
        Verifica la configuración de Git.
        
        Args:
            auto_init: Si es True, inicializa automáticamente el repositorio Git.
            
        Returns:
            bool: True si Git está configurado correctamente.
        """
        try:
            if not (self.project_root / ".git").exists():
                logger.warning("⚠️  No se encontró repositorio Git")
                if auto_init:
                    subprocess.run(["git", "init"], cwd=self.project_root, check=True)
                    subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
                    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.project_root, check=True)
                    logger.info("✨ Repositorio Git inicializado")
                    return True
                return False
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"⚠️  Error configurando Git: {e}")
            return False

    def check_requirements(self, auto_create: bool = False) -> bool:
        """
        Verifica que los archivos de requirements existan.
        
        Args:
            auto_create: Si es True, crea automáticamente los archivos de requirements.
            
        Returns:
            bool: True si los requirements están configurados correctamente.
        """
        requirements_dir = self.project_root / "requirements"
        if not requirements_dir.exists():
            logger.warning("⚠️  No se encontró directorio requirements/")
            if auto_create:
                try:
                    requirements_dir.mkdir(exist_ok=True)
                    base_reqs = [
                        "fastapi>=0.68.0",
                        "uvicorn>=0.15.0",
                        "pydantic>=1.8.2",
                        "cryptography>=3.4.7",
                        "redis>=4.0.0",
                        "sqlalchemy>=1.4.23",
                        "openai>=0.27.0",
                        "anthropic>=0.3.0",
                        "click>=8.0.0",
                        "paramiko>=3.4.0"
                    ]
                    (requirements_dir / "base.txt").write_text("\n".join(base_reqs))
                    logger.info("✨ Archivos de requirements creados")
                    return True
                except Exception as e:
                    logger.error(f"⚠️  Error creando requirements: {e}")
                    return False
            return False
        return True
        
    def get_current_version(self) -> str:
        """
        Obtiene la versión actual del proyecto.
        
        Returns:
            str: Versión actual del proyecto.
        """
        if self.version_file.exists():
            content = self.version_file.read_text()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        return "0.0.0"
        
    def validate_version(self, version: str) -> bool:
        """
        Valida el formato de la versión.
        
        Args:
            version: Versión a validar.
            
        Returns:
            bool: True si el formato es válido.
        """
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
        
    def update_version(self, new_version: str) -> bool:
        """
        Actualiza la versión en los archivos del proyecto.
        
        Args:
            new_version: Nueva versión a establecer.
            
        Returns:
            bool: True si la actualización fue exitosa.
        """
        try:
            # Actualizar __init__.py
            if self.version_file.exists():
                content = self.version_file.read_text()
                new_content = re.sub(
                    r'__version__\s*=\s*["\']([^"\']+)["\']',
                    f'__version__ = "{new_version}"',
                    content
                )
                self.version_file.write_text(new_content)
                logger.info(f"✓ Versión actualizada en {self.version_file}")
                
            # Actualizar pyproject.toml
            if self.pyproject_file.exists():
                content = self.pyproject_file.read_text()
                new_content = re.sub(
                    r'version\s*=\s*["\']([^"\']+)["\']',
                    f'version = "{new_version}"',
                    content
                )
                self.pyproject_file.write_text(new_content)
                logger.info(f"✓ Versión actualizada en {self.pyproject_file}")
                
            return True
        except Exception as e:
            logger.error(f"⚠️  Error actualizando versión: {e}")
            return False
            
    def get_pypi_credentials(self) -> Optional[Tuple[str, str]]:
        """
        Obtiene credenciales de PyPI del archivo .pypirc.
        
        Returns:
            Optional[Tuple[str, str]]: Tupla con (username, password) o None si no se encuentran.
        """
        pypirc = Path.home() / ".pypirc"
        if not pypirc.exists():
            logger.error("⚠️  No se encontró archivo .pypirc")
            logger.info("Cree el archivo ~/.pypirc con el siguiente formato:")
            logger.info("""
[pypi]
username = your_username
password = your_password
            """)
            return None
            
        config = configparser.ConfigParser()
        config.read(pypirc)
        
        if "pypi" not in config:
            logger.error("⚠️  No se encontró sección 'pypi' en .pypirc")
            return None
            
        username = config["pypi"].get("username")
        password = config["pypi"].get("password")
        
        if not username or not password:
            logger.error("⚠️  Credenciales incompletas en .pypirc")
            return None
            
        return username, password
        
    def clean_project(self) -> bool:
        """
        Limpia el proyecto antes del build.
        
        Returns:
            bool: True si la limpieza fue exitosa.
        """
        try:
            logger.info("🧹 Limpiando proyecto...")
            # Eliminar archivos de build anteriores
            for pattern in ["build/", "dist/", "*.egg-info"]:
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        path.rmdir()
                    else:
                        path.unlink()
            logger.info("✨ Proyecto limpiado correctamente")
            return True
        except Exception as e:
            logger.error(f"⚠️  Error limpiando proyecto: {e}")
            return False
        
    def build_project(self) -> bool:
        """
        Construye el proyecto.
        
        Returns:
            bool: True si el build fue exitoso.
        """
        try:
            logger.info("🏗️  Construyendo proyecto...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], check=True)
            subprocess.run([
                sys.executable, "-m", "build", "."
            ], check=True)
            logger.info("✨ Proyecto construido correctamente")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"⚠️  Error construyendo proyecto: {e}")
            return False
        
    def deploy_to_pypi(self) -> bool:
        """
        Despliega el proyecto a PyPI.
        
        Returns:
            bool: True si el despliegue fue exitoso.
        """
        try:
            logger.info("🚀 Desplegando a PyPI...")
            subprocess.run([
                sys.executable, "-m", "twine", "upload",
                "dist/*"
            ], check=True)
            logger.info("✨ Proyecto desplegado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"⚠️  Error desplegando proyecto: {e}")
            return False
        
    def run_deployment(self, 
                      new_version: str,
                      auto_install: bool = False,
                      auto_init: bool = False,
                      auto_create: bool = False) -> bool:
        """
        Ejecuta el proceso completo de despliegue.
        
        Args:
            new_version: Nueva versión a desplegar.
            auto_install: Si es True, instala automáticamente las dependencias faltantes.
            auto_init: Si es True, inicializa automáticamente el repositorio Git.
            auto_create: Si es True, crea automáticamente los archivos de requirements.
            
        Returns:
            bool: True si el despliegue fue exitoso.
        """
        try:
            # Validar versión
            if not self.validate_version(new_version):
                logger.error("⚠️  Formato de versión inválido. Use x.y.z (ej: 1.0.0)")
                return False
            
            # Verificar configuración
            deps_status = self.check_dependencies(auto_install)
            if not all(deps_status.values()):
                logger.error("⚠️  Faltan dependencias necesarias")
                return False
                
            if not self.check_git_setup(auto_init):
                logger.error("⚠️  Git no está configurado correctamente")
                return False
                
            if not self.check_requirements(auto_create):
                logger.error("⚠️  Requirements no están configurados correctamente")
                return False
            
            # Verificar credenciales
            if not self.get_pypi_credentials():
                logger.error("⚠️  Configure sus credenciales en ~/.pypirc")
                return False
            
            # Actualizar versión
            if not self.update_version(new_version):
                return False
            
            # Limpiar y construir
            if not self.clean_project() or not self.build_project():
                return False
            
            # Desplegar
            return self.deploy_to_pypi()
            
        except Exception as e:
            logger.error(f"⚠️  Error durante el despliegue: {e}")
            return False 