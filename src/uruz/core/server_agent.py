from typing import Dict, Any, List, Tuple
from time import time
from .llm_agent import LLMAgent
from ..security.vault import Vault
from ..storage.database_manager import DatabaseManager
from ..config import settings
import paramiko
import os

class ServerAgent(LLMAgent):
    """Agente especializado en tareas de servidor con acceso al vault."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.vault = Vault()
        self.db = DatabaseManager(settings.DATABASE_URL)
    
    def get_server_credentials(self) -> Dict[str, Any]:
        """Obtiene las credenciales de servidores del vault."""
        try:
            credentials = self.vault.get_credential("server_credentials")
            # Registrar acceso a credenciales
            self.db.update_credential_access("server_credentials")
            return credentials
        except KeyError:
            return {}
    
    async def execute_ssh_command(self, server_name: str, command: str) -> Tuple[str, str]:
        """Ejecuta un comando en el servidor vía SSH."""
        start_time = time()
        credentials = self.get_server_credentials()
        
        if server_name not in credentials:
            error = f"No se encontraron credenciales para el servidor {server_name}"
            self.db.log_command(
                server_name=server_name,
                command=command,
                executed_by=self.agent_id,
                status="error",
                error=error
            )
            raise ValueError(error)
        
        server_info = credentials[server_name]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Expandir el path de la clave SSH
            ssh_key = os.path.expanduser(server_info["ssh_key"])
            
            # Conectar al servidor
            ssh.connect(
                hostname=server_info["host"],
                username=server_info["username"],
                key_filename=ssh_key,
                port=server_info["port"]
            )
            
            # Ejecutar comando
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            # Registrar comando ejecutado
            status = "success" if not error else "error"
            self.db.log_command(
                server_name=server_name,
                command=command,
                executed_by=self.agent_id,
                status=status,
                output=output,
                error=error
            )
            
            return output, error
            
        finally:
            ssh.close()
            # Registrar métricas
            end_time = time()
            self.db.log_agent_metrics(
                agent_id=self.agent_id,
                request_type="ssh_command",
                processing_time=end_time - start_time,
                tokens_used=0,  # No usa tokens LLM
                success=True,
                metadata={
                    "server": server_name,
                    "command": command
                }
            )
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un mensaje usando el LLM y proporciona acceso a credenciales."""
        start_time = time()
        success = True
        error_message = None
        
        try:
            # Obtener credenciales
            credentials = self.get_server_credentials()
            
            # Agregar información de credenciales al prompt
            enhanced_prompt = f"""
            Información de servidores disponibles en el vault:
            {credentials}
            
            Solicitud del usuario:
            {message["content"]}
            
            Si el usuario solicita ejecutar comandos en el servidor, usa la función execute_ssh_command.
            Responde usando la información real de los servidores listados arriba.
            No inventes información que no esté en las credenciales.
            """
            
            response = await self.llm.generate(enhanced_prompt)
            
            # Si el mensaje incluye una solicitud de ejecutar un comando
            if "lista" in message["content"].lower() and "directorio" in message["content"].lower():
                try:
                    output, error = await self.execute_ssh_command("groovinads", "ls -l ~")
                    if error:
                        success = False
                        error_message = error
                        return {"response": f"Error ejecutando comando: {error}"}
                    return {"response": f"Contenido del directorio:\n{output}"}
                except Exception as e:
                    success = False
                    error_message = str(e)
                    return {"response": f"Error conectando al servidor: {str(e)}"}
            
            return {"response": response}
            
        except Exception as e:
            success = False
            error_message = str(e)
            raise
            
        finally:
            # Registrar métricas
            end_time = time()
            self.db.log_agent_metrics(
                agent_id=self.agent_id,
                request_type="message",
                processing_time=end_time - start_time,
                tokens_used=len(message["content"]),
                success=success,
                error_message=error_message,
                metadata={
                    "message_type": "command" if "lista" in message["content"].lower() else "query"
                }
            )
    
    async def act(self) -> List[Dict[str, Any]]:
        """Este agente no realiza acciones autónomas."""
        return [] 