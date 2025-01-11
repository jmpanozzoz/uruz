import pytest
from uruz.core.environment import Environment
from uruz.core.agent import Agent
from uruz.core.message import Message

class MockAgent(Agent):
    def __init__(self, agent_id: str, config: dict):
        super().__init__(agent_id, config)
        self.received_messages = []
        
    async def process_message(self, message):
        self.received_messages.append(message)
        return {"status": "received"}
        
    async def act(self):
        return [{"action": "mock_action"}]

@pytest.mark.asyncio
async def test_environment_agent_communication():
    env = Environment()
    
    # Crear y agregar agentes
    agent1 = MockAgent("agent1", {})
    agent2 = MockAgent("agent2", {})
    env.add_agent(agent1)
    env.add_agent(agent2)
    
    # Probar comunicación
    message = Message.create(
        sender_id="agent1",
        receiver_id="agent2",
        content={"text": "hello"}
    )
    await env.message_broker.publish(message)
    
    assert len(agent2.received_messages) == 1
    assert agent2.received_messages[0].content["text"] == "hello"

@pytest.mark.asyncio
async def test_environment_step():
    env = Environment()
    agent = MockAgent("test_agent", {})
    env.add_agent(agent)
    
    results = await env.step()
    assert len(results) == 1
    assert results[0]["action"] == "mock_action" 