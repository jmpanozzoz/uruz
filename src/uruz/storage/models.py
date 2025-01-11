from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

class CommandHistory(Base):
    """Historial de comandos ejecutados en servidores."""
    __tablename__ = "command_history"
    
    id = Column(Integer, primary_key=True)
    server_name = Column(String, nullable=False)
    command = Column(String, nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    executed_by = Column(String, nullable=False)  # ID del agente
    status = Column(String, nullable=False)  # success/error
    output = Column(String)
    error = Column(String)

class AgentMetrics(Base):
    """Métricas de uso de los agentes."""
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_type = Column(String, nullable=False)  # message/action
    processing_time = Column(Float)  # tiempo en segundos
    tokens_used = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(String)
    extra_data = Column(JSON)  # datos adicionales en formato JSON

class StoredCredential(Base):
    """Registro de credenciales almacenadas."""
    __tablename__ = "stored_credentials"
    
    id = Column(Integer, primary_key=True)
    credential_key = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    extra_data = Column(JSON)  # información adicional no sensible 