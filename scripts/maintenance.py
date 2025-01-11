#!/usr/bin/env python3
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from uruz.storage.database_manager import DatabaseManager
from uruz.security.backup import VaultBackup
from uruz.config import settings

class MaintenanceTask:
    """Tareas de mantenimiento del sistema."""
    
    def __init__(self):
        self.db = DatabaseManager(settings.DATABASE_URL)
        self.vault_backup = VaultBackup()
        
    def cleanup_old_logs(self, days: int = 30):
        """Limpia logs antiguos."""
        log_dir = Path('data/logs')
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in log_dir.glob('**/*.log.*'):
            if log_file.stat().st_mtime < cutoff.timestamp():
                log_file.unlink()
                
    def cleanup_old_metrics(self, days: int = 90):
        """Limpia métricas antiguas de la base de datos."""
        cutoff = datetime.now() - timedelta(days=days)
        with self.db.db.get_session() as session:
            session.query(self.db.AgentMetrics)\
                  .filter(self.db.AgentMetrics.timestamp < cutoff)\
                  .delete()
            session.commit()
            
    def cleanup_old_backups(self, keep: int = 10):
        """Mantiene solo los N backups más recientes."""
        backups = self.vault_backup.list_backups()
        if len(backups) > keep:
            for backup in backups[keep:]:
                base_path = os.path.join(
                    self.vault_backup.backup_dir,
                    f"vault_backup_{backup['timestamp']}"
                )
                for ext in ['.json', '.key', '.meta']:
                    try:
                        os.remove(f"{base_path}{ext}")
                    except FileNotFoundError:
                        pass
                        
    def optimize_database(self):
        """Optimiza la base de datos."""
        with self.db.db.get_session() as session:
            session.execute('VACUUM')
            session.execute('ANALYZE')
            
    def create_backup(self):
        """Crea un nuevo backup del vault."""
        self.vault_backup.create_backup()
        
    def run_all(self):
        """Ejecuta todas las tareas de mantenimiento."""
        print("Iniciando tareas de mantenimiento...")
        
        print("1. Limpiando logs antiguos...")
        self.cleanup_old_logs()
        
        print("2. Limpiando métricas antiguas...")
        self.cleanup_old_metrics()
        
        print("3. Gestionando backups...")
        self.create_backup()
        self.cleanup_old_backups()
        
        print("4. Optimizando base de datos...")
        self.optimize_database()
        
        print("Mantenimiento completado.")

if __name__ == '__main__':
    maintenance = MaintenanceTask()
    maintenance.run_all() 