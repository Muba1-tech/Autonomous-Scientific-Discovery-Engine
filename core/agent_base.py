"""Core Agent Base Class for AION X.
Provides lifecycle tracking, timeout guards, and retry mechanics for autonomous agents.
"""
import enum
import time
import uuid
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class AgentStatus(enum.Enum):
    IDLE = 'IDLE'
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    RETRYING = 'RETRYING'
    CANCELLED = 'CANCELLED'


class BaseAgent(ABC):
    """Base class for agents with safe execution, retry handling, and status tracking."""

    def __init__(self, name: str = "Agent", max_retries: int = 2, timeout: float = 30.0):
        self.id = str(uuid.uuid4())
        self.name = name
        self.max_retries = max_retries
        self.timeout = timeout
        self.status = AgentStatus.IDLE
        self.run_count = 0
        self.last_error: Optional[str] = None
        self.last_execution_time: float = 0.0

    @abstractmethod
    def _execute(self, *args, **kwargs) -> Any:
        """Internal execution method to be overridden by subclasses."""
        raise NotImplementedError

    def run_safe(self, *args, **kwargs) -> Any:
        """Execute agent with retry logic and timeout checking."""
        self.status = AgentStatus.RUNNING
        self.run_count = 0
        last_exception = None

        while self.run_count <= self.max_retries:
            self.run_count += 1
            start_time = time.time()
            try:
                res = self._execute(*args, **kwargs)
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    raise TimeoutError(f"Agent {self.name} timed out after {elapsed:.2f}s (limit: {self.timeout}s)")
                
                self.last_execution_time = elapsed
                self.status = AgentStatus.IDLE
                return res
            except TimeoutError as te:
                self.last_error = str(te)
                self.status = AgentStatus.FAILED
                raise te
            except Exception as e:
                last_exception = e
                self.last_error = str(e)
                if self.run_count <= self.max_retries:
                    self.status = AgentStatus.RETRYING
                else:
                    self.status = AgentStatus.FAILED
                    raise last_exception

        self.status = AgentStatus.FAILED
        if last_exception:
            raise last_exception

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "run_count": self.run_count,
            "last_error": self.last_error,
            "last_execution_time": self.last_execution_time,
        }
