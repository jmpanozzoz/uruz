from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración global del framework."""
    
    # Versión del framework
    VERSION: str = "0.1.3"
    
    # Configuración del proyecto
    URUZ_ENV: str = "development"
    URUZ_PROJECT_NAME: str = "uruz"
    
    # Directorios del proyecto
    URUZ_AGENTS_DIR: str = "agents"
    URUZ_DATA_DIR: str = "data"
    URUZ_CONFIG_DIR: str = "config"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Configuración de seguridad
    SSH_KEY_PATH: str = "~/.ssh/id_rsa"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///data/storage/uruz.db"
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "anthropic"
    LLM_CONFIG: Dict[str, Any] = {
        "model": "claude-3-haiku-20240307",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings() 