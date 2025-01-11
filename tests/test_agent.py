import pytest
from uruz.core.agent import Agent
from uruz.security.vault import Vault

class TestAgent(Agent):
    async def process_message(self, message):
        return {"echo": message}
    
    async def act(self):
        return [{"action": "test"}]

@pytest.mark.asyncio
async def test_agent_process_message():
    agent = TestAgent("test-agent", {})
    message = {"content": "hello"}
    response = await agent.process_message(message)
    assert response["echo"] == message

@pytest.mark.asyncio
async def test_agent_act():
    agent = TestAgent("test-agent", {})
    actions = await agent.act()
    assert len(actions) == 1
    assert actions[0]["action"] == "test" 