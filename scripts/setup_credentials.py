import os
from uruz.security.vault import Vault
from uruz.config import settings

def setup_credentials():
    # Inicializar el vault
    vault = Vault()
    
    # Expandir el path de la clave SSH
    ssh_key_path = os.path.expanduser(settings.SSH_KEY_PATH)
    
    # Almacenar credenciales usando variables de entorno
    server_credentials = {
        "groovinads": {
            "host": "whm01.groovinads.com",
            "username": "groovinads",
            "ssh_key": ssh_key_path,
            "port": 22
        }
    }
    
    # Guardar credenciales en el vault
    vault.store_credential("server_credentials", server_credentials)
    print(f"Credenciales almacenadas exitosamente en el vault")
    print(f"Usando clave SSH en: {ssh_key_path}")

if __name__ == "__main__":
    setup_credentials()