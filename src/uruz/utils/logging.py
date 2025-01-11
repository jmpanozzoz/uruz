import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..config import settings

class AgentLogger:
    """Logger especializado para agentes."""
    
    def __init__(self, agent_id: str, log_dir: Optional[str] = None):
        self.agent_id = agent_id
        self.log_dir = log_dir or os.path.join('data', 'logs', 'agents')
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo con rotación
        log_file = os.path.join(self.log_dir, f"{agent_id}.log")
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Formato detallado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def log_action(self, action: str, details: dict):
        """Registra una acción del agente."""
        self.logger.info(f"Action: {action} - Details: {details}")
        
    def log_error(self, error: str, context: dict):
        """Registra un error del agente."""
        self.logger.error(f"Error: {error} - Context: {context}")
        
    def log_metric(self, metric_type: str, value: float, metadata: dict):
        """Registra una métrica del agente."""
        self.logger.debug(f"Metric: {metric_type}={value} - Metadata: {metadata}")

def setup_logging():
    """Configura el logging global."""
    log_dir = os.path.join('data', 'logs')
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Logger principal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                os.path.join(log_dir, 'uruz.log'),
                maxBytes=10*1024*1024,
                backupCount=5
            )
        ]
    )
    
    # Logger para accesos
    access_logger = logging.getLogger('uruz.access')
    access_logger.setLevel(logging.INFO)
    access_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        when='midnight',
        interval=1,
        backupCount=30
    )
    access_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    access_logger.addHandler(access_handler)
    
    return logging.getLogger('uruz')

logger = setup_logging() 