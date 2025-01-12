"""
Environment module for Uruz Framework.
"""
import os
from pathlib import Path
from typing import Dict, Any, List
import yaml
from ..config import settings

class Environment:
    """Manages the environment and agents for Uruz Framework."""
    
    def __init__(self):
        """Initialize the environment."""
        self.agents = {}
        self.agents_dir = os.getenv('URUZ_AGENTS_DIR', 'agents')
        self.data_dir = os.getenv('URUZ_DATA_DIR', 'data')
        self.config_dir = os.getenv('URUZ_CONFIG_DIR', 'config')
        
        # Asegurar que existan los directorios
        for dir_path in [self.agents_dir, self.data_dir, self.config_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Cargar agentes existentes
        self._load_agents()
    
    def _load_agents(self):
        """Load agents from YAML files."""
        if not os.path.exists(self.agents_dir):
            return
            
        for filename in os.listdir(self.agents_dir):
            if filename.endswith('.yaml'):
                agent_path = os.path.join(self.agents_dir, filename)
                try:
                    with open(agent_path) as f:
                        config = yaml.safe_load(f)
                        agent_id = os.path.splitext(filename)[0]
                        
                        # Importar dinámicamente la clase del agente
                        if 'agent_class' in config.get('config', {}):
                            module_path, class_name = config['config']['agent_class'].rsplit('.', 1)
                            module = __import__(module_path, fromlist=[class_name])
                            agent_class = getattr(module, class_name)
                        else:
                            from ..core.llm_agent import LLMAgent
                            agent_class = LLMAgent
                        
                        # Crear instancia del agente
                        agent = agent_class(agent_id, config.get('config', {}))
                        self.add_agent(agent)
                        
                except Exception as e:
                    print(f"Error loading agent {filename}: {e}")
    
    def add_agent(self, agent: Any) -> None:
        """Add an agent to the environment."""
        self.agents[agent.agent_id] = agent
    
    def get_agent(self, agent_id: str) -> Any:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all agent IDs."""
        return list(self.agents.keys())
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the environment."""
        return {
            'agents': self.list_agents(),
            'config': {
                'agents_dir': self.agents_dir,
                'data_dir': self.data_dir,
                'config_dir': self.config_dir
            }
        }
    
    def save_agent_config(self, agent_id: str, config: Dict[str, Any]) -> None:
        """Save agent configuration to YAML file."""
        config_path = os.path.join(self.agents_dir, f"{agent_id}.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False) 