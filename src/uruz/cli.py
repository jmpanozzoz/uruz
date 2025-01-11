import click
from uruz.config import settings
from uruz.utils.logging import setup_logging, logger
from uruz.core.environment import Environment
from uruz.security.vault import Vault
from uruz.core.llm_agent import LLMAgent
from uruz.core.server_agent import ServerAgent
from uruz.storage.database_manager import DatabaseManager
import uvicorn
import os
import sys
import yaml

env = Environment()

@click.group()
def cli():
    """CLI para el framework Uruz."""
    setup_logging()

def init_cli():
    """Inicializa y registra todos los comandos CLI."""
    cli.add_command(serve)
    cli.add_command(list_agents)
    cli.add_command(status)
    cli.add_command(show_metrics)
    cli.add_command(show_history)
    cli.add_command(maintenance)
    cli.add_command(backup_vault)
    cli.add_command(restore_vault)
    cli.add_command(clear_cache)
    cli.add_command(show_queues)
    return cli

@cli.command()
@click.option('--host', default=settings.API_HOST, help='Host para el servidor API')
@click.option('--port', default=settings.API_PORT, help='Puerto para el servidor API')
@click.option('--debug', is_flag=True, help='Modo debug')
def serve(host, port, debug):
    """Inicia el servidor API."""
    logger.info(f"Iniciando servidor en {host}:{port}")
    uvicorn.run(
        "uruz.api.server:app",
        host=host,
        port=port,
        reload=debug
    )

@cli.command()
@click.option("--name", required=True, help="Nombre del agente")
@click.option("--type", required=True, help="Tipo de agente (llm/server/simple)")
def create_agent(name: str, type: str):
    """Crea un nuevo agente."""
    try:
        if type == "server":
            config = {
                "name": name,
                "type": type,
                "provider": "anthropic",
                "config": {
                    "model": "claude-3-haiku-20240307",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "system_prompt": "Eres un asistente especializado en tareas de servidor.",
                    "use_vault": True,
                    "agent_class": "uruz.core.server_agent.ServerAgent",
                    "anthropic_api_key": settings.ANTHROPIC_API_KEY
                }
            }
        else:
            config = {
                "name": name,
                "type": type,
                "provider": "anthropic",
                "config": {
                    "model": "claude-3-haiku-20240307",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "system_prompt": "Eres un asistente amigable y servicial.",
                    "anthropic_api_key": settings.ANTHROPIC_API_KEY
                }
            }
        
        # Crear el directorio agents si no existe
        os.makedirs("agents", exist_ok=True)
        
        # Guardar configuración
        with open(f"agents/{name}.yaml", "w") as f:
            yaml.dump(config, f)
        
        # Crear y registrar el agente
        if type == "llm":
            agent = LLMAgent(name, config["config"])
            env.add_agent(agent)
        elif type == "server":
            agent = ServerAgent(name, config["config"])
            env.add_agent(agent)
        
        click.echo(f"Agente {name} creado exitosamente")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def list_agents():
    """Lista todos los agentes disponibles."""
    try:
        env = Environment()
        agents = env.get_state()["agents"]
        click.echo("Agentes activos:")
        for agent in agents:
            click.echo(f"  - {agent}")
    except Exception as e:
        logger.error(f"Error listando agentes: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--check-deps', is_flag=True, help='Verificar dependencias')
def status(check_deps):
    """Muestra el estado del sistema."""
    try:
        click.echo("Estado del sistema:")
        
        # Verificar configuración
        click.echo("\nConfiguración:")
        click.echo(f"  Database URL: {settings.DATABASE_URL}")
        click.echo(f"  Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        # Verificar vault
        vault = Vault()
        click.echo("\nVault:")
        click.echo("  Status: Activo")
        
        if check_deps:
            click.echo("\nDependencias:")
            import pkg_resources
            for pkg in pkg_resources.working_set:
                click.echo(f"  {pkg.key} {pkg.version}")
                
    except Exception as e:
        logger.error(f"Error verificando estado: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def show_metrics():
    """Muestra las métricas de uso de los agentes."""
    try:
        db = DatabaseManager(settings.DATABASE_URL)
        metrics = db.get_agent_metrics()
        
        click.echo("\nMétricas de Agentes:")
        for metric in metrics:
            click.echo(f"\nAgente: {metric.agent_id}")
            click.echo(f"Timestamp: {metric.timestamp}")
            click.echo(f"Tipo: {metric.request_type}")
            click.echo(f"Tiempo: {metric.processing_time:.2f}s")
            click.echo(f"Tokens: {metric.tokens_used}")
            click.echo(f"Estado: {'✓' if metric.success else '✗'}")
            if metric.error_message:
                click.echo(f"Error: {metric.error_message}")
    except Exception as e:
        click.echo(f"Error obteniendo métricas: {e}", err=True)

@cli.command()
@click.option('--server', help='Filtrar por servidor')
@click.option('--limit', default=10, help='Número máximo de registros')
def show_history(server: str, limit: int):
    """Muestra el historial de comandos ejecutados."""
    try:
        db = DatabaseManager(settings.DATABASE_URL)
        history = db.get_command_history(server_name=server, limit=limit)
        
        click.echo("\nHistorial de Comandos:")
        for cmd in history:
            click.echo(f"\nServidor: {cmd.server_name}")
            click.echo(f"Comando: {cmd.command}")
            click.echo(f"Ejecutado por: {cmd.executed_by}")
            click.echo(f"Fecha: {cmd.executed_at}")
            click.echo(f"Estado: {'✓' if cmd.status == 'success' else '✗'}")
            if cmd.output:
                click.echo(f"Salida: {cmd.output[:100]}...")
            if cmd.error:
                click.echo(f"Error: {cmd.error}")
    except Exception as e:
        click.echo(f"Error obteniendo historial: {e}", err=True)

@cli.command()
@click.option('--days', default=30, help='Días de antigüedad para limpieza')
def maintenance(days: int):
    """Ejecuta tareas de mantenimiento."""
    try:
        from scripts.maintenance import MaintenanceTask
        task = MaintenanceTask()
        task.run_all()
        click.echo("Mantenimiento completado exitosamente")
    except Exception as e:
        logger.error(f"Error en mantenimiento: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def backup_vault():
    """Crea un backup del vault."""
    try:
        from uruz.security.backup import VaultBackup
        backup = VaultBackup()
        path = backup.create_backup()
        click.echo(f"Backup creado en: {path}")
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('backup_path')
def restore_vault(backup_path: str):
    """Restaura un backup del vault."""
    try:
        from uruz.security.backup import VaultBackup
        backup = VaultBackup()
        backup.restore_backup(backup_path)
        click.echo("Backup restaurado exitosamente")
    except Exception as e:
        logger.error(f"Error restaurando backup: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--pattern', default="*", help='Patrón para limpiar caché')
def clear_cache(pattern: str):
    """Limpia el caché de Redis."""
    try:
        from uruz.cache.redis_provider import RedisProvider
        redis = RedisProvider()
        count = redis.clear_cache(pattern)
        click.echo(f"Se eliminaron {count} claves del caché")
    except Exception as e:
        logger.error(f"Error limpiando caché: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def show_queues():
    """Muestra el estado de las colas de Redis."""
    try:
        from uruz.cache.redis_provider import RedisProvider
        redis = RedisProvider()
        
        click.echo("\nEstado de las Colas:")
        for queue in ["tasks", "events"]:
            length = redis.get_queue_length(queue)
            click.echo(f"  {queue}: {length} elementos")
            
    except Exception as e:
        logger.error(f"Error mostrando colas: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    init_cli()
    cli() 