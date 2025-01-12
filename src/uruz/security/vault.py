from typing import Dict, Any
from cryptography.fernet import Fernet
import json
import os

class Vault:
    """Sistema seguro para almacenar y gestionar credenciales."""
    
    def __init__(self, encryption_key: str = None):
        self.vault_file = "data/vault.json"
        os.makedirs(os.path.dirname(self.vault_file), exist_ok=True)
        
        # Generar o cargar clave de encriptación
        self.key_file = "data/vault.key"
        if os.path.exists(self.key_file) and not encryption_key:
            with open(self.key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = encryption_key or Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.encryption_key)
        
        self.fernet = Fernet(self.encryption_key)
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, bytes]:
        """Carga las credenciales desde el archivo."""
        if os.path.exists(self.vault_file):
            with open(self.vault_file, 'r') as f:
                try:
                    return {k: v.encode() for k, v in json.load(f).items()}
                except json.JSONDecodeError:
                    return {}
        return {}
    
    def _save_credentials(self):
        """Guarda las credenciales en el archivo."""
        with open(self.vault_file, 'w') as f:
            json.dump({k: v.decode() for k, v in self.credentials.items()}, f)
    
    def store_credential(self, key: str, value: Any):
        """Almacena una credencial de forma segura."""
        encrypted_value = self.fernet.encrypt(json.dumps(value).encode())
        self.credentials[key] = encrypted_value
        self._save_credentials()
    
    def get_credential(self, key: str) -> Any:
        """Recupera una credencial almacenada."""
        if key not in self.credentials:
            raise KeyError(f"Credencial no encontrada: {key}")
        
        encrypted_value = self.credentials[key]
        decrypted_value = self.fernet.decrypt(encrypted_value)
        return json.loads(decrypted_value) 
    
    def list_credentials(self) -> Dict[str, Any]:
        """Lista todas las credenciales almacenadas."""
        return {k: self.get_credential(k) for k in self.credentials.keys()} 