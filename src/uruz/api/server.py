import os
import yaml
from fastapi import FastAPI
from uruz.config import settings
from uruz.core.environment import Environment
from uruz.core.llm_agent import LLMAgent
from uruz.core.server_agent import ServerAgent

app = FastAPI(title="Uruz Framework API")
env = Environment()

def load_agents():
    """Carga los agentes desde los archivos YAML."""
    agents_dir = "agents"
    if not os.path.exists(agents_dir):
        return
    
    for filename in os.listdir(agents_dir):
        if filename.endswith(".yaml"):
            with open(os.path.join(agents_dir, filename)) as f:
                config = yaml.safe_load(f)
                
                agent_id = os.path.splitext(filename)[0]
                if config["type"] == "llm":
                    agent = LLMAgent(agent_id, config["config"])
                    env.add_agent(agent)
                elif config["type"] == "server":
                    agent = ServerAgent(agent_id, config["config"])
                    env.add_agent(agent)

# Cargar agentes al iniciar
load_agents()

@app.get("/")
async def root():
    return {"message": "Uruz Framework API"}

@app.get("/agents")
async def list_agents():
    return {"agents": env.list_agents()}

@app.post("/agents/{agent_id}/message")
async def send_message(agent_id: str, message: dict):
    try:
        agent = env.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        response = await agent.process_message(message)
        return {"response": response["response"]}
    except Exception as e:
        return {"error": f"Error generando respuesta: {str(e)}"}

@app.get("/status")
async def get_status():
    return {
        "status": "active",
        "agents": len(env.list_agents()),
        "config": {
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "debug": settings.API_DEBUG
        }
    }
