#!/usr/bin/env python3
"""Script para desplegar el proyecto a PyPI."""

import os
import sys
import subprocess
import logging
from pathlib import Path
import configparser
import re
from typing import Optional, Tuple
from importlib.metadata import version, PackageNotFoundError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

REQUIRED_PACKAGES = {
    'build': 'build>=0.10.0',
    'twine': 'twine>=4.0.2',
    'setuptools': 'setuptools>=68.0.0',
    'wheel': 'wheel>=0.40.0',
    'setuptools_scm': 'setuptools_scm>=8.0.0'
}

class PyPIDeployer:
    """Gestiona el despliegue a PyPI."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.version_file = self.project_root / "src" / "uruz" / "__init__.py"
        self.pyproject_file = self.project_root / "pyproject.toml"
        
    def check_dependencies(self) -> bool:
        """Verifica que las dependencias necesarias estén instaladas."""
        missing_packages = []
        
        for package, requirement in REQUIRED_PACKAGES.items():
            try:
                current_version = version(package)
                logger.info(f"Encontrado {package} versión {current_version}")
            except PackageNotFoundError:
                missing_packages.append(requirement)
                
        if missing_packages:
            logger.warning("Faltan dependencias necesarias:")
            for package in missing_packages:
                logger.warning(f"  - {package}")
                
            install = input("¿Instalar dependencias faltantes? [Y/n]: ")
            if install.lower() != 'n':
                try:
                    for package in missing_packages:
                        logger.info(f"Instalando {package}...")
                        subprocess.run([
                            sys.executable, "-m", "pip", "install",
                            package
                        ], check=True)
                    logger.info("Dependencias instaladas correctamente")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error instalando dependencias: {e}")
                    return False
            return False
        return True

    def check_git_setup(self) -> bool:
        """Verifica la configuración de Git."""
        try:
            if not (self.project_root / ".git").exists():
                logger.warning("No se encontró repositorio Git")
                init = input("¿Inicializar repositorio Git? [Y/n]: ")
                if init.lower() != 'n':
                    subprocess.run(["git", "init"], cwd=self.project_root, check=True)
                    subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
                    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.project_root, check=True)
                    logger.info("Repositorio Git inicializado")
                    return True
                return False
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error configurando Git: {e}")
            return False

    def check_requirements(self) -> bool:
        """Verifica que los archivos de requirements existan."""
        requirements_dir = self.project_root / "requirements"
        if not requirements_dir.exists():
            logger.warning("No se encontró directorio requirements/")
            create = input("¿Crear directorio y archivos de requirements? [Y/n]: ")
            if create.lower() != 'n':
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
                    logger.info("Archivos de requirements creados")
                    return True
                except Exception as e:
                    logger.error(f"Error creando requirements: {e}")
                    return False
            return False
        return True
        
    def get_current_version(self) -> str:
        """Obtiene la versión actual del proyecto."""
        if self.version_file.exists():
            content = self.version_file.read_text()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        return "0.0.0"
        
    def validate_version(self, version: str) -> bool:
        """Valida el formato de la versión."""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
        
    def update_version(self, new_version: str) -> None:
        """Actualiza la versión en los archivos del proyecto."""
        # Actualizar __init__.py
        if self.version_file.exists():
            content = self.version_file.read_text()
            new_content = re.sub(
                r'__version__\s*=\s*["\']([^"\']+)["\']',
                f'__version__ = "{new_version}"',
                content
            )
            self.version_file.write_text(new_content)
            logger.info(f"Versión actualizada en {self.version_file}")
            
        # Actualizar pyproject.toml
        if self.pyproject_file.exists():
            content = self.pyproject_file.read_text()
            new_content = re.sub(
                r'version\s*=\s*["\']([^"\']+)["\']',
                f'version = "{new_version}"',
                content
            )
            self.pyproject_file.write_text(new_content)
            logger.info(f"Versión actualizada en {self.pyproject_file}")
            
    def get_pypi_credentials(self) -> Optional[Tuple[str, str]]:
        """Obtiene credenciales de PyPI del archivo .pypirc."""
        pypirc = Path.home() / ".pypirc"
        if not pypirc.exists():
            logger.error("No se encontró archivo .pypirc")
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
            logger.error("No se encontró sección 'pypi' en .pypirc")
            return None
            
        username = config["pypi"].get("username")
        password = config["pypi"].get("password")
        
        if not username or not password:
            logger.error("Credenciales incompletas en .pypirc")
            return None
            
        return username, password
        
    def clean_project(self) -> None:
        """Limpia el proyecto antes del build."""
        logger.info("Limpiando proyecto...")
        clean_script = self.project_root / "scripts" / "clean.py"
        subprocess.run([sys.executable, str(clean_script)], check=True)
        
    def build_project(self) -> None:
        """Construye el proyecto."""
        logger.info("Construyendo proyecto...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], check=True)
        subprocess.run([
            sys.executable, "-m", "build", "."
        ], check=True)
        
    def deploy_to_pypi(self) -> None:
        """Despliega el proyecto a PyPI."""
        logger.info("Desplegando a PyPI...")
        subprocess.run([
            sys.executable, "-m", "twine", "upload",
            "dist/*"
        ], check=True)
        
    def run(self) -> None:
        """Ejecuta el proceso de despliegue."""
        try:
            # Verificar dependencias y configuración
            if not all([
                self.check_dependencies(),
                self.check_git_setup(),
                self.check_requirements()
            ]):
                logger.error("Falta configuración necesaria")
                sys.exit(1)
            
            # Verificar credenciales
            if not self.get_pypi_credentials():
                logger.error("Configure sus credenciales en ~/.pypirc")
                sys.exit(1)
                
            # Obtener versión actual
            current_version = self.get_current_version()
            logger.info(f"Versión actual: {current_version}")
            
            # Solicitar nueva versión
            while True:
                new_version = input("Nueva versión (x.y.z) o Enter para salir: ")
                if not new_version:
                    sys.exit(0)
                if self.validate_version(new_version):
                    break
                logger.error("Formato inválido. Use x.y.z (ej: 1.0.0)")
            
            # Confirmar despliegue
            confirm = input(f"¿Desplegar versión {new_version} a PyPI? [y/N]: ")
            if confirm.lower() != 'y':
                logger.info("Despliegue cancelado")
                sys.exit(0)
                
            # Actualizar versión
            self.update_version(new_version)
            
            # Limpiar y construir
            self.clean_project()
            self.build_project()
            
            # Desplegar
            self.deploy_to_pypi()
            
            logger.info(f"Versión {new_version} desplegada exitosamente")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error en el proceso: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            sys.exit(1)

def update_version_in_file(file_path: Path, current_version: str, new_version: str):
    content = file_path.read_text()
    print(f"📄 Contenido original de {file_path}:")
    print(content[:200])  # Mostrar primeros 200 caracteres
    
    if file_path.name == "__init__.py":
        pattern = r'__version__\s*=\s*["\']([^"\']+)["\']'
        replacement = f'__version__ = "{new_version}"'
    elif file_path.name == "pyproject.toml":
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        replacement = f'version = "{new_version}"'
    elif file_path.name == "setup.py":
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        replacement = f'version="{new_version}"'
    else:
        print(f"❌ Tipo de archivo no soportado: {file_path}")
        return
    
    # Buscar el patrón antes de reemplazar
    match = re.search(pattern, content)
    if not match:
        print(f"❌ No se encontró el patrón de versión en {file_path}")
        print(f"🔍 Buscando: {pattern}")
        return
    
    updated_content = re.sub(pattern, replacement, content)
    
    # Verificar que el contenido cambió
    if content == updated_content:
        print(f"⚠️ El contenido no cambió en {file_path}")
    else:
        file_path.write_text(updated_content)
        print(f"✓ Actualizada versión en {file_path} de {current_version} a {new_version}")
        print("📄 Nuevo contenido:")
        print(updated_content[:200])

def get_current_version():
    init_file = Path("src/uruz/__init__.py")
    if not init_file.exists():
        print(f"⚠️  No se encontró el archivo {init_file}")
        return "0.1.0"
    
    content = init_file.read_text()
    print("📄 Contenido de __init__.py:")
    print(content[:200])
    
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not version_match:
        print("⚠️  No se encontró la versión en __init__.py")
        return "0.1.0"
    
    version = version_match.group(1)
    print(f"📌 Versión encontrada: {version}")
    return version

def main():
    # Obtener versión actual
    current_version = get_current_version()
    print(f"📦 Versión actual: {current_version}")
    
    # Solicitar nueva versión
    while True:
        new_version = input(f"📝 Ingrese la nueva versión (actual: {current_version}): ").strip()
        if re.match(r'^\d+\.\d+\.\d+$', new_version):
            break
        print("❌ Formato inválido. Use x.y.z (ejemplo: 0.1.3)")
    
    # Confirmar acción
    confirm = input(f"🔍 ¿Confirma actualizar a versión {new_version}? [y/N]: ")
    if confirm.lower() != 'y':
        print("❌ Operación cancelada")
        return
    
    # Actualizar versión en archivos
    files_to_update = [
        Path("src/uruz/__init__.py"),
        Path("pyproject.toml"),
        Path("setup.py")
    ]
    
    for file in files_to_update:
        if not file.exists():
            print(f"⚠️  No se encontró el archivo {file}")
            continue
        update_version_in_file(file, current_version, new_version)
    
    # Limpiar distribuciones anteriores
    print("🧹 Limpiando distribuciones anteriores...")
    subprocess.run(["rm", "-rf", "dist/", "build/", "*.egg-info/"], check=True)
    
    # Construir y publicar
    print("🔨 Construyendo distribución...")
    subprocess.run(["python", "-m", "build"], check=True)
    
    print("📤 Publicando en PyPI...")
    subprocess.run(["python", "-m", "twine", "upload", "dist/*"], check=True)
    
    print(f"\n✅ Paquete desplegado exitosamente con versión {new_version}")

if __name__ == "__main__":
    main() 