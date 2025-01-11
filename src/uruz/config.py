from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración global del framework."""
    
    # Configuración de base de datos
    DATABASE_URL: str = "sqlite:///./data/uruz.db"
    
    # Configuración de Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Configuración de API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # Configuración de LLM
    DEFAULT_LLM_PROVIDER: str = "anthropic"
    LLM_CONFIG: Dict[str, Any] = {
        "model": "claude-3-haiku-20240307",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Server Credentials
    SSH_KEY_PATH: str = "~/.ssh/id_rsa"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings() 