import pytest
import time
from unittest.mock import Mock, patch
from core.agent_base import BaseAgent, AgentStatus

class DummyAgent(BaseAgent):
    def _execute(self, task):
        if task == "fail":
            raise ValueError("Intentional failure")
        return f"Task {task} completed"

def test_base_agent_instantiation():
    agent = DummyAgent(name="TestAgent", max_retries=3, timeout=5)
    assert agent.name == "TestAgent"
    assert agent.status == AgentStatus.IDLE
    assert agent.max_retries == 3

def test_agent_lifecycle_and_run_safe():
    agent = DummyAgent(name="TestAgent")
    result = agent.run_safe("success")
    assert result == "Task success completed"
    assert agent.status == AgentStatus.IDLE

def test_agent_retry_logic():
    agent = DummyAgent(name="TestAgent", max_retries=2)
    with pytest.raises(ValueError):
        agent.run_safe("fail")
    assert agent.status == AgentStatus.FAILED
    assert agent.run_count == 3  # Initial + 2 retries

def test_agent_timeout_tracking():
    agent = DummyAgent(name="TestAgent", timeout=1)
    
    # Mocking time.time to simulate timeout
    with patch('time.time', side_effect=[0, 2, 4]):
        with pytest.raises(TimeoutError):
            agent.run_safe("timeout_task")

def test_agent_serialization():
    agent = DummyAgent(name="TestAgent", max_retries=2)
    serialized = agent.to_dict()
    assert serialized["name"] == "TestAgent"
    assert serialized["status"] == "IDLE"
    assert "id" in serialized
