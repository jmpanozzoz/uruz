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
from typing import List
from .security.credentials import setup_credentials, list_credentials

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
    cli.add_command(init)
    cli.add_command(setup_creds)
    cli.add_command(list_creds)
    cli.add_command(check_system)
    cli.add_command(start)
    cli.add_command(deploy)
    cli.add_command(clean)
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

@cli.group()
def maintenance():
    """Comandos de mantenimiento del sistema."""
    pass

@maintenance.command()
@click.option('--days', default=30, help='Días de antigüedad para considerar un log como obsoleto')
def cleanup_logs(days: int):
    """Limpia logs antiguos del sistema."""
    try:
        from uruz.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager()
        files_removed = manager.cleanup_logs(days)
        if files_removed >= 0:
            click.echo("✅ Limpieza de logs completada")
        else:
            click.echo("⚠️  No se pudieron limpiar los logs", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@maintenance.command()
@click.option('--days', default=90, help='Días de antigüedad para considerar una métrica como obsoleta')
def cleanup_metrics(days: int):
    """Limpia métricas antiguas de la base de datos."""
    try:
        from uruz.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager()
        records_removed = manager.cleanup_metrics(days)
        if records_removed >= 0:
            click.echo("✅ Limpieza de métricas completada")
        else:
            click.echo("⚠️  No se pudieron limpiar las métricas", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@maintenance.command()
@click.option('--keep', default=10, help='Número de backups a mantener')
def cleanup_backups(keep: int):
    """Mantiene solo los N backups más recientes."""
    try:
        from uruz.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager()
        files_removed = manager.cleanup_backups(keep)
        if files_removed >= 0:
            click.echo("✅ Limpieza de backups completada")
        else:
            click.echo("⚠️  No se pudieron limpiar los backups", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@maintenance.command()
def optimize_db():
    """Optimiza la base de datos."""
    try:
        from uruz.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager()
        if manager.optimize_database():
            click.echo("✅ Base de datos optimizada")
        else:
            click.echo("⚠️  No se pudo optimizar la base de datos", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@maintenance.command()
def create_backup():
    """Crea un nuevo backup del vault."""
    try:
        from uruz.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager()
        backup_path = manager.create_backup()
        if backup_path:
            click.echo(f"✅ Backup creado en: {backup_path}")
        else:
            click.echo("⚠️  No se pudo crear el backup", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@maintenance.command()
@click.option('--log-days', default=30, help='Días de antigüedad para logs')
@click.option('--metric-days', default=90, help='Días de antigüedad para métricas')
@click.option('--keep-backups', default=10, help='Número de backups a mantener')
def run_all(log_days: int, metric_days: int, keep_backups: int):
    """Ejecuta todas las tareas de mantenimiento."""
    try:
        from uruz.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager()
        results = manager.run_maintenance(log_days, metric_days, keep_backups)
        
        # Mostrar resultados
        click.echo("\n🔧 Resultados del mantenimiento:")
        for task, success in results.items():
            status = "✅" if success else "❌"
            click.echo(f"{status} {task}")
        
        # Verificar si todas las tareas fueron exitosas
        if all(results.values()):
            click.echo("\n✨ Mantenimiento completado exitosamente")
        else:
            click.echo("\n⚠️  Algunas tareas fallaron", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
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

@cli.command()
@click.option('--path', default='.', help='Ruta donde inicializar el proyecto')
@click.option('--name', prompt='Nombre del proyecto', help='Nombre del proyecto')
@click.option('--api/--no-api', default=True, help='Inicializar con servidor API')
@click.option('--redis/--no-redis', default=True, help='Configurar Redis')
def init(path: str, name: str, api: bool, redis: bool):
    """Inicializa un nuevo proyecto con Uruz Framework."""
    try:
        from uruz.project import ProjectManager
        
        click.echo(f"🚀 Inicializando proyecto {name}...")
        
        # Crear estructura del proyecto
        project = ProjectManager(path, name)
        project.init_project(
            with_api=api,
            with_redis=redis
        )
        
        click.echo("✨ Proyecto inicializado exitosamente!")
        click.echo("\n📁 Estructura creada:")
        project.show_structure()
        
        click.echo("\n📝 Próximos pasos:")
        click.echo("1. cd " + name)
        click.echo("2. Edita .env con tus credenciales")
        click.echo("3. Crea tus agentes en agents/")
        click.echo("4. Ejecuta 'uruz serve' para iniciar")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command(name='setup-credentials', help="Configura las credenciales del sistema")
def setup_creds():
    try:
        setup_credentials()
    except Exception as e:
        logger.error(f"❌ Error configurando credenciales: {str(e)}")
        sys.exit(1)

@cli.command(name='list-credentials', help="Lista las credenciales almacenadas")
def list_creds():
    try:
        list_credentials()
    except Exception as e:
        logger.error(f"❌ Error listando credenciales: {str(e)}")
        sys.exit(1)

@cli.command()
def check_system():
    """Verifica el estado del sistema y sus dependencias."""
    try:
        from uruz.utils.system_check import check_system as check
        issues = check()
        
        if not issues:
            click.echo("✅ Sistema verificado correctamente")
        else:
            click.echo("⚠️  Se encontraron problemas:")
            for issue in issues:
                click.echo(f"  - {issue}")
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--force', is_flag=True, help='Forzar inicio incluso si hay errores')
def start(force: bool):
    """Inicia todos los servicios necesarios del sistema."""
    try:
        from uruz.utils.system_setup import SystemSetup
        
        setup = SystemSetup()
        if not force:
            # Verificar sistema primero
            from uruz.utils.system_check import check_system
            issues = check_system()
            if issues:
                click.echo("⚠️  Se encontraron problemas en el sistema:")
                for issue in issues:
                    click.echo(f"  - {issue}")
                if not click.confirm("¿Desea continuar de todos modos?"):
                    sys.exit(1)
        
        setup.start_services()
        click.echo("✨ Servicios iniciados correctamente")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.group()
def deploy():
    """Comandos de despliegue del proyecto."""
    pass

@deploy.command()
@click.option('--auto-install', is_flag=True, help='Instalar dependencias faltantes automáticamente')
def check_deps(auto_install: bool):
    """Verifica las dependencias necesarias para el despliegue."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        status = manager.check_dependencies(auto_install)
        
        click.echo("\n📦 Estado de las dependencias:")
        for package, installed in status.items():
            status_icon = "✅" if installed else "❌"
            click.echo(f"{status_icon} {package}")
            
        if not all(status.values()):
            click.echo("\n⚠️  Faltan algunas dependencias", err=True)
            sys.exit(1)
        else:
            click.echo("\n✨ Todas las dependencias están instaladas")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@deploy.command()
@click.option('--auto-init', is_flag=True, help='Inicializar Git automáticamente')
def check_git(auto_init: bool):
    """Verifica la configuración de Git."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        if manager.check_git_setup(auto_init):
            click.echo("✅ Git configurado correctamente")
        else:
            click.echo("⚠️  Git no está configurado correctamente", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@deploy.command()
@click.option('--auto-create', is_flag=True, help='Crear requirements automáticamente')
def check_reqs(auto_create: bool):
    """Verifica los archivos de requirements."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        if manager.check_requirements(auto_create):
            click.echo("✅ Requirements configurados correctamente")
        else:
            click.echo("⚠️  Requirements no están configurados correctamente", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@deploy.command()
def check_pypi():
    """Verifica las credenciales de PyPI."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        if manager.get_pypi_credentials():
            click.echo("✅ Credenciales de PyPI configuradas correctamente")
        else:
            click.echo("⚠️  Credenciales de PyPI no configuradas", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@deploy.command()
def clean():
    """Limpia los archivos de build."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        if manager.clean_project():
            click.echo("✅ Proyecto limpiado correctamente")
        else:
            click.echo("⚠️  Error limpiando el proyecto", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@deploy.command()
def build():
    """Construye el proyecto."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        if manager.build_project():
            click.echo("✅ Proyecto construido correctamente")
        else:
            click.echo("⚠️  Error construyendo el proyecto", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@deploy.command()
@click.argument('version')
@click.option('--auto-install', is_flag=True, help='Instalar dependencias faltantes automáticamente')
@click.option('--auto-init', is_flag=True, help='Inicializar Git automáticamente')
@click.option('--auto-create', is_flag=True, help='Crear requirements automáticamente')
@click.option('--force', is_flag=True, help='No pedir confirmación')
def release(version: str, auto_install: bool, auto_init: bool, auto_create: bool, force: bool):
    """Despliega una nueva versión a PyPI."""
    try:
        from uruz.utils.deployment import DeploymentManager
        manager = DeploymentManager()
        
        # Obtener versión actual
        current_version = manager.get_current_version()
        click.echo(f"\n📦 Versión actual: {current_version}")
        click.echo(f"📦 Nueva versión: {version}")
        
        # Confirmar despliegue
        if not force:
            if not click.confirm("\n¿Desea continuar con el despliegue?"):
                click.echo("Despliegue cancelado")
                return
        
        # Ejecutar despliegue
        if manager.run_deployment(version, auto_install, auto_init, auto_create):
            click.echo("\n✨ Proyecto desplegado correctamente")
        else:
            click.echo("\n⚠️  Error durante el despliegue", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.group()
def clean():
    """Comandos de limpieza del proyecto."""
    pass

@clean.command(name="all")
@click.option('--categories', '-c', multiple=True, help='Categorías específicas a limpiar')
def clean_all(categories: List[str]):
    """Limpia todos los archivos temporales."""
    try:
        from uruz.utils.cleaner import ProjectCleaner
        cleaner = ProjectCleaner()
        
        results = cleaner.clean_all(categories if categories else None)
        
        # Mostrar resultados
        click.echo("\n🧹 Resultados de la limpieza:")
        total = 0
        for category, count in results.items():
            click.echo(f"✓ {category}: {count} archivos")
            total += count
        click.echo(f"\n✨ Total: {total} archivos limpiados")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@clean.command()
@click.argument('category')
def category(category: str):
    """Limpia archivos de una categoría específica."""
    try:
        from uruz.utils.cleaner import ProjectCleaner
        cleaner = ProjectCleaner()
        
        count = cleaner.clean_by_category(category)
        if count >= 0:
            click.echo(f"✨ {count} archivos limpiados de la categoría {category}")
        else:
            click.echo(f"⚠️  Categoría {category} no válida", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@clean.command()
def setup():
    """Configura el proyecto limpio y listo para usar."""
    try:
        from uruz.utils.cleaner import ProjectCleaner
        cleaner = ProjectCleaner()
        
        if cleaner.setup_project():
            click.echo("✨ Proyecto configurado correctamente")
        else:
            click.echo("⚠️  Error configurando el proyecto", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@clean.command()
def list_categories():
    """Lista las categorías disponibles para limpieza."""
    try:
        from uruz.utils.cleaner import ProjectCleaner
        cleaner = ProjectCleaner()
        
        click.echo("\n📋 Categorías disponibles:")
        for category in cleaner.CLEANUP_PATTERNS.keys():
            patterns = cleaner.CLEANUP_PATTERNS[category]
            click.echo(f"\n{category}:")
            for pattern in patterns:
                click.echo(f"  - {pattern}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    init_cli()
    cli() 