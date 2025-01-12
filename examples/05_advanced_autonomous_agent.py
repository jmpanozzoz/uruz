"""
Ejemplo de un agente autónomo avanzado que monitorea y optimiza un sistema de base de datos.
"""

import asyncio
import sqlite3
import psutil
from datetime import datetime, timedelta
from uruz.core.environment import Environment
from uruz.core.agent import Agent
from uruz.security.vault import Vault

class DatabaseOptimizer(Agent):
    """Agente que monitorea y optimiza una base de datos SQLite."""
    
    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config)
        self.db_path = config.get("db_path", "data/storage/uruz.db")
        self.check_interval = config.get("check_interval", 300)  # 5 minutos
        self.last_check = None
        self.last_optimization = None
        self.optimization_interval = timedelta(hours=config.get("optimization_interval", 24))
        self.metrics = {
            "queries_analyzed": 0,
            "optimizations_performed": 0,
            "space_saved": 0
        }
    
    async def process_message(self, message: dict) -> dict:
        """Procesa mensajes para consultar estado o ejecutar acciones específicas."""
        content = message.get("content", "").lower()
        
        if content == "status":
            return {"response": await self._get_status()}
        elif content == "optimize":
            return {"response": await self._force_optimization()}
        elif content == "metrics":
            return {"response": self._get_metrics()}
        
        return {"response": """Comandos disponibles:
- status: muestra el estado actual
- optimize: fuerza una optimización
- metrics: muestra métricas de rendimiento"""}
    
    async def act(self) -> list:
        """Realiza monitoreo y optimización automática."""
        now = datetime.now()
        actions = []
        
        # Verificar si es tiempo de monitorear
        if not self.last_check or (now - self.last_check).seconds >= self.check_interval:
            self.last_check = now
            status = await self._analyze_database()
            actions.extend(status)
        
        # Verificar si es tiempo de optimizar
        if not self.last_optimization or (now - self.last_optimization) >= self.optimization_interval:
            if await self._should_optimize():
                optimization_results = await self._optimize_database()
                actions.extend(optimization_results)
                self.last_optimization = now
        
        return actions if actions else [{"status": "monitoring"}]
    
    async def _analyze_database(self) -> list:
        """Analiza el estado de la base de datos."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener estadísticas
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size = (page_count * page_size) / (1024 * 1024)  # MB
            
            # Verificar fragmentación
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            conn.close()
            self.metrics["queries_analyzed"] += 1
            
            alerts = []
            if db_size > 100:  # Si DB > 100MB
                alerts.append({
                    "type": "alert",
                    "level": "warning",
                    "message": f"Base de datos grande: {db_size:.2f}MB"
                })
            
            if integrity != "ok":
                alerts.append({
                    "type": "alert",
                    "level": "error",
                    "message": "Problemas de integridad detectados"
                })
            
            return alerts
            
        except Exception as e:
            return [{
                "type": "alert",
                "level": "error",
                "message": f"Error analizando base de datos: {str(e)}"
            }]
    
    async def _should_optimize(self) -> bool:
        """Determina si se debe realizar una optimización."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar espacio libre
            cursor.execute("PRAGMA freelist_count")
            free_pages = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_count")
            total_pages = cursor.fetchone()[0]
            
            conn.close()
            
            # Optimizar si hay más de 10% de páginas libres
            return (free_pages / total_pages) > 0.1
            
        except Exception:
            return False
    
    async def _optimize_database(self) -> list:
        """Optimiza la base de datos."""
        try:
            initial_size = os.path.getsize(self.db_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Optimizar
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            
            conn.close()
            
            final_size = os.path.getsize(self.db_path)
            space_saved = (initial_size - final_size) / (1024 * 1024)  # MB
            
            self.metrics["optimizations_performed"] += 1
            self.metrics["space_saved"] += space_saved
            
            return [{
                "type": "optimization",
                "message": f"Optimización completada. Espacio ahorrado: {space_saved:.2f}MB"
            }]
            
        except Exception as e:
            return [{
                "type": "alert",
                "level": "error",
                "message": f"Error optimizando base de datos: {str(e)}"
            }]
    
    async def _get_status(self) -> str:
        """Obtiene el estado actual del sistema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size = (page_count * page_size) / (1024 * 1024)  # MB
            
            cursor.execute("PRAGMA freelist_count")
            free_pages = cursor.fetchone()[0]
            free_space = (free_pages * page_size) / (1024 * 1024)  # MB
            
            conn.close()
            
            return f"""Estado de la Base de Datos:
- Tamaño total: {db_size:.2f}MB
- Espacio libre: {free_space:.2f}MB
- Última revisión: {self.last_check.strftime('%Y-%m-%d %H:%M:%S')}
- Última optimización: {self.last_optimization.strftime('%Y-%m-%d %H:%M:%S') if self.last_optimization else 'Nunca'}"""
            
        except Exception as e:
            return f"Error obteniendo estado: {str(e)}"
    
    async def _force_optimization(self) -> str:
        """Fuerza una optimización inmediata."""
        results = await self._optimize_database()
        return "\n".join(result["message"] for result in results)
    
    def _get_metrics(self) -> str:
        """Obtiene las métricas de rendimiento."""
        return f"""Métricas de Rendimiento:
- Consultas analizadas: {self.metrics['queries_analyzed']}
- Optimizaciones realizadas: {self.metrics['optimizations_performed']}
- Espacio total ahorrado: {self.metrics['space_saved']:.2f}MB"""

async def main():
    # 1. Inicializar entorno
    env = Environment()
    
    # 2. Configurar agente
    agent_config = {
        "db_path": "data/storage/uruz.db",
        "check_interval": 10,  # 10 segundos para demo
        "optimization_interval": 1  # 1 hora
    }
    
    # 3. Crear y registrar agente
    agent = DatabaseOptimizer("db_optimizer", config=agent_config)
    env.add_agent(agent)
    
    # 4. Simular operación
    print("\n🔄 Iniciando monitoreo de base de datos...")
    
    # 4.1 Consultar estado inicial
    response = await agent.process_message({"content": "status"})
    print(f"\nEstado Inicial:\n{response['response']}")
    
    # 4.2 Ejecutar ciclos de monitoreo
    print("\n📊 Ejecutando ciclos de monitoreo...")
    for i in range(3):
        print(f"\nCiclo {i+1}:")
        results = await env.step()
        for result in results:
            if result.get("type") == "alert":
                print(f"⚠️  {result['message']}")
            elif result.get("type") == "optimization":
                print(f"🔧 {result['message']}")
            else:
                print("✓ Monitoreo activo")
        await asyncio.sleep(agent_config["check_interval"])
    
    # 4.3 Mostrar métricas finales
    response = await agent.process_message({"content": "metrics"})
    print(f"\nMétricas Finales:\n{response['response']}")

if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de agente autónomo avanzado...")
    asyncio.run(main())
    print("\n✨ Ejemplo completado exitosamente!")