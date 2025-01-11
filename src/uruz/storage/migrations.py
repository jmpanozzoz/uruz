from alembic import context
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from datetime import datetime
from ..config import settings
from .models import Base

class DatabaseMigration:
    """Manejador de migraciones de base de datos."""
    
    def __init__(self, connection_string: str = settings.DATABASE_URL):
        self.engine = create_engine(connection_string)
        self.config = Config()
        self.config.set_main_option("script_location", "migrations")
        
    def create_migration(self, message: str):
        """Crea una nueva migración."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script = ScriptDirectory.from_config(self.config)
        script.generate_revision(
            rev_id=timestamp,
            message=message,
            refresh=True
        )
        
    def upgrade(self):
        """Aplica todas las migraciones pendientes."""
        with self.engine.connect() as connection:
            context = MigrationContext.configure(connection)
            script = ScriptDirectory.from_config(self.config)
            
            def upgrade(rev, context):
                return script._upgrade_revs(script.get_current_head(), rev)
                
            with context.begin_transaction():
                context.run_migrations(upgrade) 