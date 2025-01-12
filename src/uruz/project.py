"""
Módulo para gestionar la estructura y configuración de proyectos Uruz.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any
import yaml
from .config import settings

class ProjectManager:
    """Gestor de proyectos Uruz."""
    
    DEFAULT_STRUCTURE = {
        'agents': {},           # Configuraciones de agentes
        'data': {              # Datos y almacenamiento
            'logs': {},
            'backups': {},
            'storage': {}
        },
        'config': {           # Configuraciones
            'environments': {
                'development.yaml': '''
name: development
redis:
  host: localhost
  port: 6379
database:
  url: sqlite:///data/storage/uruz.db
logging:
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
''',
                'production.yaml': '''
name: production
redis:
  host: localhost
  port: 6379
database:
  url: sqlite:///data/storage/uruz.db
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
'''
            }
        }
    }
    
    def __init__(self, base_path: str, project_name: str):
        """
        Inicializa el gestor de proyectos.
        
        Args:
            base_path: Ruta base donde crear el proyecto
            project_name: Nombre del proyecto
        """
        self.base_path = Path(base_path)
        self.project_name = project_name
        self.project_path = self.base_path / project_name
    
    def init_project(self, with_api: bool = True, with_redis: bool = True):
        """
        Inicializa un nuevo proyecto.
        
        Args:
            with_api: Si se debe inicializar con soporte API
            with_redis: Si se debe configurar Redis
        """
        # Crear estructura base
        self._create_directory_structure()
        
        # Crear archivos de configuración
        self._create_env_file(with_redis)
        self._create_example_agent()
        
        if with_api:
            self._create_api_files()
    
    def _create_directory_structure(self):
        """Crea la estructura de directorios del proyecto."""
        if self.project_path.exists():
            raise ValueError(f"El directorio {self.project_path} ya existe")
        
        # Crear directorios
        for dir_name, contents in self.DEFAULT_STRUCTURE.items():
            dir_path = self.project_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Crear subdirectorios y archivos
            if isinstance(contents, dict):
                self._create_nested_structure(dir_path, contents)
    
    def _create_nested_structure(self, base_path: Path, structure: Dict[str, Any]):
        """Crea estructura anidada de directorios y archivos."""
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                path.mkdir(exist_ok=True)
                self._create_nested_structure(path, content)
            elif isinstance(content, str):
                with open(path, 'w') as f:
                    f.write(content.strip() + '\n')
    
    def _create_env_file(self, with_redis: bool):
        """Crea el archivo .env con la configuración básica."""
        env_content = f"""# Configuración de Uruz Framework
URUZ_ENV=development
URUZ_PROJECT_NAME={self.project_name}

# Directorios del proyecto
URUZ_AGENTS_DIR=agents
URUZ_DATA_DIR=data
URUZ_CONFIG_DIR=config

# API Keys (reemplazar con tus claves)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Configuración de seguridad
SSH_KEY_PATH=~/.ssh/id_rsa
"""
        if with_redis:
            env_content += """
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
"""
        
        with open(self.project_path / '.env', 'w') as f:
            f.write(env_content)
        
        # Crear .env.example
        shutil.copy(self.project_path / '.env', self.project_path / '.env.example')
    
    def _create_example_agent(self):
        """Crea un archivo de ejemplo para un agente."""
        example_agent = {
            'name': 'example_agent',
            'type': 'llm',
            'provider': 'anthropic',
            'config': {
                'model': 'claude-3-haiku-20240307',
                'temperature': 0.7,
                'max_tokens': 1024,
                'system_prompt': 'Eres un asistente amigable y servicial.',
                'use_vault': True
            }
        }
        
        with open(self.project_path / 'agents' / 'example_agent.yaml', 'w') as f:
            yaml.dump(example_agent, f, default_flow_style=False)
    
    def _create_api_files(self):
        """Crea archivos necesarios para el servidor API."""
        api_dir = self.project_path / 'api'
        api_dir.mkdir(exist_ok=True)
        
        # main.py para FastAPI
        main_content = '''from fastapi import FastAPI
from uruz.core.environment import Environment

app = FastAPI(title=f"{os.getenv('URUZ_PROJECT_NAME')} API")
env = Environment()

@app.get("/")
async def root():
    return {"message": f"Welcome to {os.getenv('URUZ_PROJECT_NAME')}"}

@app.get("/agents")
async def list_agents():
    return {"agents": env.list_agents()}
'''
        
        with open(api_dir / 'main.py', 'w') as f:
            f.write(main_content)
    
    def show_structure(self):
        """Muestra la estructura del proyecto creado."""
        def print_tree(path: Path, prefix: str = '', is_last: bool = True):
            print(prefix + ('└── ' if is_last else '├── ') + path.name)
            
            if path.is_dir():
                entries = list(path.iterdir())
                entries.sort(key=lambda x: (not x.is_dir(), x.name))
                
                for i, entry in enumerate(entries):
                    is_last_entry = i == len(entries) - 1
                    print_tree(entry, prefix + ('    ' if is_last else '│   '), is_last_entry)
        
        print_tree(self.project_path) 