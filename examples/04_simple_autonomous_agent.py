"""
Ejemplo de un agente autónomo simple que monitorea un sistema y reporta su estado.
"""

import asyncio
import psutil
from datetime import datetime
from uruz.core.environment import Environment
from uruz.core.agent import Agent

class SystemMonitorAgent(Agent):
    """Agente que monitorea recursos del sistema y reporta su estado."""
    
    def __init__(self, name: str, config: dict = None):
        super().__init__(name, config)
        self.check_interval = config.get("check_interval", 5)  # segundos
        self.last_check = None
        self.thresholds = config.get("thresholds", {
            "cpu": 80,  # porcentaje
            "memory": 80,  # porcentaje
            "disk": 80   # porcentaje
        })
    
    async def process_message(self, message: dict) -> dict:
        """Procesa mensajes para consultar el estado del sistema."""
        if message.get("content") == "status":
            return {"response": await self._get_system_status()}
        return {"response": "Comando no reconocido. Use 'status' para ver el estado del sistema."}
    
    async def act(self) -> list:
        """Monitorea el sistema periódicamente y reporta alertas si es necesario."""
        now = datetime.now()
        if not self.last_check or (now - self.last_check).seconds >= self.check_interval:
            self.last_check = now
            status = await self._get_system_status()
            alerts = self._check_alerts(status)
            return alerts if alerts else [{"status": "normal"}]
        return []
    
    async def _get_system_status(self) -> str:
        """Obtiene el estado actual del sistema."""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        return f"""Estado del Sistema:
- CPU: {cpu}%
- Memoria: {memory}%
- Disco: {disk}%
- Tiempo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _check_alerts(self, status: str) -> list:
        """Verifica si hay alertas basadas en los umbrales configurados."""
        alerts = []
        metrics = {
            line.split(':')[0].strip('-').strip(): float(line.split(':')[1].strip('%'))
            for line in status.split('\n')[1:4]
        }
        
        for resource, value in metrics.items():
            if value > self.thresholds.get(resource.lower(), 80):
                alerts.append({
                    "type": "alert",
                    "level": "warning",
                    "message": f"¡Alerta! {resource} al {value}% (umbral: {self.thresholds[resource.lower()]}%)"
                })
        
        return alerts

async def main():
    # 1. Inicializar entorno
    env = Environment()
    
    # 2. Configurar agente
    agent_config = {
        "check_interval": 3,  # revisar cada 3 segundos
        "thresholds": {
            "cpu": 70,
            "memory": 75,
            "disk": 85
        }
    }
    
    # 3. Crear y registrar agente
    agent = SystemMonitorAgent("monitor", config=agent_config)
    env.add_agent(agent)
    
    # 4. Simular monitoreo
    print("\n🔄 Iniciando monitoreo del sistema...")
    
    # 4.1 Consultar estado actual
    response = await agent.process_message({"content": "status"})
    print(f"\nEstado Inicial:\n{response['response']}")
    
    # 4.2 Ejecutar ciclos de monitoreo
    print("\n📊 Ejecutando ciclos de monitoreo...")
    for _ in range(3):
        results = await env.step()
        for result in results:
            if result.get("type") == "alert":
                print(f"\n⚠️  {result['message']}")
            else:
                print(f"\n✓ Sistema normal: {datetime.now().strftime('%H:%M:%S')}")
        await asyncio.sleep(agent_config["check_interval"])

if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de agente autónomo...")
    asyncio.run(main())
    print("\n✨ Ejemplo completado exitosamente!") 