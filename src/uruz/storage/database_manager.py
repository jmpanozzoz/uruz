from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SQLAlchemyProvider
from .models import Base, CommandHistory, AgentMetrics, StoredCredential

class DatabaseManager:
    """Manejador de operaciones de base de datos."""
    
    def __init__(self, connection_string: str):
        self.db = SQLAlchemyProvider(connection_string)
        self.db.connect()
        # Crear tablas si no existen
        Base.metadata.create_all(self.db.engine)
    
    def log_command(self, server_name: str, command: str, executed_by: str,
                   status: str, output: Optional[str] = None, error: Optional[str] = None) -> None:
        """Registra un comando ejecutado."""
        with self.db.get_session() as session:
            command_log = CommandHistory(
                server_name=server_name,
                command=command,
                executed_by=executed_by,
                status=status,
                output=output,
                error=error
            )
            session.add(command_log)
            session.commit()
    
    def log_agent_metrics(self, agent_id: str, request_type: str,
                         processing_time: float, tokens_used: int,
                         success: bool = True, error_message: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """Registra métricas de uso de un agente."""
        with self.db.get_session() as session:
            metrics = AgentMetrics(
                agent_id=agent_id,
                request_type=request_type,
                processing_time=processing_time,
                tokens_used=tokens_used,
                success=success,
                error_message=error_message,
                extra_data=metadata or {}
            )
            session.add(metrics)
            session.commit()
    
    def register_credential(self, key: str, description: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """Registra una nueva credencial."""
        with self.db.get_session() as session:
            credential = StoredCredential(
                credential_key=key,
                description=description,
                extra_data=metadata or {}
            )
            session.add(credential)
            session.commit()
    
    def update_credential_access(self, key: str) -> None:
        """Actualiza el registro de acceso a una credencial."""
        with self.db.get_session() as session:
            credential = session.query(StoredCredential).filter_by(credential_key=key).first()
            if credential:
                credential.last_accessed = datetime.utcnow()
                credential.access_count += 1
                session.commit()
    
    def get_command_history(self, server_name: Optional[str] = None,
                          limit: int = 100) -> List[CommandHistory]:
        """Obtiene el historial de comandos."""
        with self.db.get_session() as session:
            query = session.query(CommandHistory)
            if server_name:
                query = query.filter_by(server_name=server_name)
            return query.order_by(CommandHistory.executed_at.desc()).limit(limit).all()
    
    def get_agent_metrics(self, agent_id: Optional[str] = None,
                         from_date: Optional[datetime] = None,
                         to_date: Optional[datetime] = None) -> List[AgentMetrics]:
        """Obtiene métricas de uso de los agentes."""
        with self.db.get_session() as session:
            query = session.query(AgentMetrics)
            if agent_id:
                query = query.filter_by(agent_id=agent_id)
            if from_date:
                query = query.filter(AgentMetrics.timestamp >= from_date)
            if to_date:
                query = query.filter(AgentMetrics.timestamp <= to_date)
            return query.order_by(AgentMetrics.timestamp.desc()).all()
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        self.db.disconnect() 