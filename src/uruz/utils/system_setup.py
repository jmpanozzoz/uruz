"""
Módulo para configuración y inicio del sistema.
"""
import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from ..config import settings
from ..utils.logging import logger

class SystemSetup:
    """Clase para gestionar la configuración y inicio del sistema."""
    
    def __init__(self):
        """Inicializa el gestor de configuración del sistema."""
        self.os_type = platform.system().lower()
        self.is_wsl = "microsoft" in platform.uname().release.lower()
        self.project_root = Path.cwd()
    
    def start_services(self):
        """Inicia todos los servicios necesarios según el sistema operativo."""
        logger.info("🚀 Iniciando servicios del sistema...")
        
        # Verificar estructura del proyecto
        self._check_project_structure()
        
        # Configurar entorno virtual
        self._setup_venv()
        
        # Verificar dependencias del sistema
        self._check_system_dependencies()
        
        # Configurar y iniciar Redis
        self._setup_redis()
        
        # Configurar base de datos
        self._setup_database()
        
        # Verificar credenciales
        self._check_credentials()
        
        logger.info("✨ Servicios iniciados correctamente")
    
    def _check_project_structure(self):
        """Verifica y crea la estructura básica del proyecto."""
        required_dirs = [
            settings.URUZ_AGENTS_DIR,
            settings.URUZ_DATA_DIR,
            settings.URUZ_CONFIG_DIR,
            Path(settings.URUZ_DATA_DIR) / "logs",
            Path(settings.URUZ_DATA_DIR) / "storage",
            Path(settings.URUZ_DATA_DIR) / "vault",
        ]
        
        for dir_path in required_dirs:
            path = Path(dir_path)
            if not path.exists():
                logger.info(f"📁 Creando directorio: {path}")
                path.mkdir(parents=True, exist_ok=True)
    
    def _check_system_dependencies(self):
        """Verifica e instala las dependencias del sistema según el OS."""
        logger.info("🔍 Verificando dependencias del sistema...")
        
        if self.os_type == "darwin":  # macOS
            self._check_homebrew()
        elif self.os_type == "linux":
            self._check_linux_dependencies()
        elif self.os_type == "windows":
            self._check_wsl()
    
    def _check_homebrew(self):
        """Verifica la instalación de Homebrew en macOS."""
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("⚠️  Homebrew no encontrado")
            logger.info("📥 Instalando Homebrew...")
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            subprocess.run(install_cmd, shell=True, check=True)
    
    def _check_linux_dependencies(self):
        """Verifica las dependencias necesarias en Linux."""
        try:
            subprocess.run(["python3-config", "--prefix"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("⚠️  Dependencias de desarrollo de Python no encontradas")
            if os.path.exists("/etc/debian_version"):
                logger.info("📥 Instalando dependencias...")
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "python3-dev", "build-essential", "-y"], check=True)
            elif os.path.exists("/etc/redhat-release"):
                subprocess.run(["sudo", "yum", "install", "python3-devel", "gcc", "-y"], check=True)
    
    def _check_wsl(self):
        """Verifica la instalación de WSL en Windows."""
        if not self.is_wsl:
            logger.warning("⚠️  WSL no detectado")
            logger.info("Para instalar WSL:")
            logger.info("1. Ejecuta: wsl --install")
            logger.info("2. Reinicia el sistema")
            logger.info("3. Vuelve a ejecutar este comando")
            sys.exit(1)
    
    def _check_credentials(self):
        """Verifica la configuración de credenciales."""
        if not os.path.exists(".env"):
            logger.warning("⚠️  Archivo .env no encontrado")
            logger.info("📝 Ejecuta 'uruz setup-credentials' para configurar las credenciales")
            return False
        
        # Verificar API keys
        with open(".env") as f:
            env_content = f.read()
            if "your-key-here" in env_content:
                logger.warning("⚠️  Credenciales no configuradas en .env")
                logger.info("📝 Ejecuta 'uruz setup-credentials' para configurar las credenciales")
                return False
        
        return True

    def _setup_venv(self):
        """Configura el entorno virtual."""
        if not os.path.exists("venv"):
            logger.info("📦 Creando entorno virtual...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Activar entorno virtual
        if self.os_type == "windows":
            activate_script = "venv\\Scripts\\activate.bat"
        else:
            activate_script = "venv/bin/activate"
        
        if os.path.exists(activate_script):
            if self.os_type == "windows":
                os.system(f"call {activate_script}")
            else:
                os.system(f"source {activate_script}")
    
    def _setup_redis(self):
        """Configura e inicia Redis según el sistema operativo."""
        if not settings.REDIS_HOST or not settings.REDIS_PORT:
            return
        
        logger.info("🔍 Verificando Redis...")
        
        if self.os_type == "darwin":  # macOS
            self._setup_redis_macos()
        elif self.os_type == "linux":
            self._setup_redis_linux()
        elif self.os_type == "windows":
            self._setup_redis_windows()
    
    def _setup_redis_macos(self):
        """Configura Redis en macOS."""
        try:
            result = subprocess.run(["brew", "list", "redis"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.info("⚙️  Instalando Redis...")
                subprocess.run(["brew", "install", "redis"], check=True)
            
            subprocess.run(["brew", "services", "start", "redis"], check=True)
            logger.info("✅ Redis iniciado correctamente")
        except subprocess.CalledProcessError as e:
            logger.error(f"⚠️  Error configurando Redis: {e}")
            sys.exit(1)
    
    def _setup_redis_linux(self):
        """Configura Redis en Linux."""
        try:
            result = subprocess.run(["which", "redis-server"], capture_output=True)
            if result.returncode != 0:
                logger.info("⚙️  Instalando Redis...")
                if os.path.exists("/etc/debian_version"):
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "redis-server", "-y"], check=True)
                elif os.path.exists("/etc/redhat-release"):
                    subprocess.run(["sudo", "yum", "install", "redis", "-y"], check=True)
            
            subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
            logger.info("✅ Redis iniciado correctamente")
        except subprocess.CalledProcessError as e:
            logger.error(f"⚠️  Error configurando Redis: {e}")
            sys.exit(1)
    
    def _setup_redis_windows(self):
        """Configura Redis en Windows (usando WSL)."""
        if not self.is_wsl:
            logger.error("⚠️  Redis en Windows requiere WSL")
            sys.exit(1)
        
        try:
            subprocess.run(["wsl", "sudo", "apt", "update"], check=True)
            subprocess.run(["wsl", "sudo", "apt", "install", "redis-server", "-y"], check=True)
            subprocess.run(["wsl", "sudo", "service", "redis-server", "start"], check=True)
            logger.info("✅ Redis iniciado correctamente en WSL")
        except subprocess.CalledProcessError as e:
            logger.error(f"⚠️  Error configurando Redis en WSL: {e}")
            sys.exit(1)
    
    def _setup_database(self):
        """Configura la base de datos."""
        db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
        if not db_path.parent.exists():
            logger.info(f"📁 Creando directorio para base de datos: {db_path.parent}")
            db_path.parent.mkdir(parents=True)
        
        logger.info("✅ Base de datos configurada correctamente") 