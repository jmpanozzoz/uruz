from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

class DatabaseProvider(ABC):
    """Clase base para proveedores de base de datos."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establece la conexión con la base de datos."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Cierra la conexión con la base de datos."""
        pass

class SQLAlchemyProvider(DatabaseProvider):
    """Implementación de proveedor de base de datos usando SQLAlchemy."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.engine = None
        self.SessionLocal = None
    
    def connect(self) -> None:
        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def disconnect(self) -> None:
        if self.engine:
            self.engine.dispose()
    
    def get_session(self) -> Session:
        """Obtiene una sesión de base de datos."""
        if not self.SessionLocal:
            raise RuntimeError("Database not connected")
        return self.SessionLocal() 