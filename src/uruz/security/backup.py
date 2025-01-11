import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from .vault import Vault
from ..config import settings

class VaultBackup:
    """Manejador de backups del vault."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        self.vault = Vault()
        self.backup_dir = backup_dir or os.path.join('data', 'backups', 'vault')
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> str:
        """Crea un nuevo backup del vault."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"vault_backup_{timestamp}")
        
        # Copiar archivos del vault
        shutil.copy2('data/vault.json', f"{backup_path}.json")
        shutil.copy2('data/vault.key', f"{backup_path}.key")
        
        # Registrar metadata del backup
        metadata = {
            "timestamp": timestamp,
            "version": settings.VERSION,
            "credentials_count": len(self.vault.list_credentials())
        }
        
        with open(f"{backup_path}.meta", 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return backup_path
    
    def restore_backup(self, backup_path: str):
        """Restaura un backup específico."""
        if not all(os.path.exists(f"{backup_path}{ext}") 
                  for ext in ['.json', '.key', '.meta']):
            raise ValueError("Backup incompleto o corrupto")
        
        # Restaurar archivos
        shutil.copy2(f"{backup_path}.json", 'data/vault.json')
        shutil.copy2(f"{backup_path}.key", 'data/vault.key')
        
    def list_backups(self):
        """Lista todos los backups disponibles."""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.meta'):
                with open(os.path.join(self.backup_dir, file)) as f:
                    metadata = json.load(f)
                backups.append(metadata)
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True) 