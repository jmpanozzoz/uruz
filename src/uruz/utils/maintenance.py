"""
Módulo para tareas de mantenimiento del sistema.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from ..storage.database_manager import DatabaseManager
from ..security.backup import VaultBackup
from ..config import settings
from ..utils.logging import logger
from sqlalchemy.sql import text

class MaintenanceManager:
    """Gestor de tareas de mantenimiento del sistema."""
    
    def __init__(self):
        """Inicializa el gestor de mantenimiento."""
        self.db = DatabaseManager(settings.DATABASE_URL)
        self.vault_backup = VaultBackup()
    
    def cleanup_logs(self, days: int = 30) -> int:
        """
        Limpia logs antiguos.
        
        Args:
            days: Días de antigüedad para considerar un log como obsoleto.
            
        Returns:
            int: Número de archivos eliminados.
        """
        logger.info(f"🧹 Limpiando logs más antiguos que {days} días...")
        log_dir = Path('data/logs')
        if not log_dir.exists():
            logger.warning("⚠️  Directorio de logs no encontrado")
            return 0
            
        cutoff = datetime.now() - timedelta(days=days)
        files_removed = 0
        
        for log_file in log_dir.glob('**/*.log.*'):
            try:
                if log_file.stat().st_mtime < cutoff.timestamp():
                    log_file.unlink()
                    files_removed += 1
            except OSError as e:
                logger.error(f"⚠️  Error eliminando {log_file}: {e}")
        
        logger.info(f"✨ {files_removed} archivos de log eliminados")
        return files_removed
    
    def cleanup_metrics(self, days: int = 90) -> int:
        """
        Limpia métricas antiguas de la base de datos.
        
        Args:
            days: Días de antigüedad para considerar una métrica como obsoleta.
            
        Returns:
            int: Número de registros eliminados.
        """
        logger.info(f"🧹 Limpiando métricas más antiguas que {days} días...")
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            with self.db.db.get_session() as session:
                result = session.query(self.db.AgentMetrics)\
                              .filter(self.db.AgentMetrics.timestamp < cutoff)\
                              .delete()
                session.commit()
                logger.info(f"✨ {result} registros de métricas eliminados")
                return result
        except Exception as e:
            logger.error(f"⚠️  Error limpiando métricas: {e}")
            return 0
    
    def cleanup_backups(self, keep: int = 10) -> int:
        """
        Mantiene solo los N backups más recientes.
        
        Args:
            keep: Número de backups a mantener.
            
        Returns:
            int: Número de backups eliminados.
        """
        logger.info(f"🧹 Manteniendo los {keep} backups más recientes...")
        backups = self.vault_backup.list_backups()
        removed = 0
        
        if len(backups) > keep:
            for backup in backups[keep:]:
                try:
                    base_path = os.path.join(
                        self.vault_backup.backup_dir,
                        f"vault_backup_{backup['timestamp']}"
                    )
                    for ext in ['.json', '.key', '.meta']:
                        try:
                            os.remove(f"{base_path}{ext}")
                            removed += 1
                        except FileNotFoundError:
                            pass
                except Exception as e:
                    logger.error(f"⚠️  Error eliminando backup: {e}")
        
        logger.info(f"✨ {removed} archivos de backup eliminados")
        return removed
    
    def optimize_database(self) -> bool:
        """
        Optimiza la base de datos.
        
        Returns:
            bool: True si la optimización fue exitosa, False en caso contrario.
        """
        logger.info("🔧 Optimizando base de datos...")
        try:
            with self.db.db.get_session() as session:
                session.execute(text('VACUUM'))
                session.execute(text('ANALYZE'))
            logger.info("✨ Base de datos optimizada")
            return True
        except Exception as e:
            logger.error(f"⚠️  Error optimizando base de datos: {e}")
            return False
    
    def create_backup(self) -> Optional[str]:
        """
        Crea un nuevo backup del vault.
        
        Returns:
            Optional[str]: Ruta del backup creado o None si hubo un error.
        """
        logger.info("💾 Creando backup del vault...")
        try:
            backup_path = self.vault_backup.create_backup()
            logger.info(f"✨ Backup creado en: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"⚠️  Error creando backup: {e}")
            return None
    
    def run_maintenance(self, 
                       log_days: int = 30,
                       metric_days: int = 90,
                       keep_backups: int = 10) -> Dict[str, bool]:
        """
        Ejecuta todas las tareas de mantenimiento.
        
        Args:
            log_days: Días de antigüedad para logs.
            metric_days: Días de antigüedad para métricas.
            keep_backups: Número de backups a mantener.
            
        Returns:
            Dict[str, bool]: Estado de cada tarea ejecutada.
        """
        results = {
            "logs": False,
            "metrics": False,
            "backups": False,
            "database": False,
            "new_backup": False
        }
        
        try:
            # Limpiar logs
            results["logs"] = self.cleanup_logs(log_days) >= 0
            
            # Limpiar métricas
            results["metrics"] = self.cleanup_metrics(metric_days) >= 0
            
            # Gestionar backups
            results["backups"] = self.cleanup_backups(keep_backups) >= 0
            results["new_backup"] = self.create_backup() is not None
            
            # Optimizar base de datos
            results["database"] = self.optimize_database()
            
            return results
        except Exception as e:
            logger.error(f"⚠️  Error durante el mantenimiento: {e}")
            return results 