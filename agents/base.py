import enum
import uuid
import time
import traceback
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import datetime

logger = logging.getLogger('aion.agents')

class AgentStatus(enum.Enum):
    """Enumeration representing the execution state of an agent."""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    RETRYING = 'RETRYING'
    SKIPPED = 'SKIPPED'
    CANCELLED = 'CANCELLED'

@dataclass
class AgentContext:
    """Standardized input context for all agents.
    
    This dataclass holds all the necessary context, data, and configurations 
    that an agent might need during its execution.
    """
    mission_id: str = ''
    research_id: str = ''
    domain: str = ''
    research_goal: str = ''
    papers: List[Dict[str, Any]] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    gaps: List[Dict[str, Any]] = field(default_factory=list)
    context_text: str = ''
    config: Dict[str, Any] = field(default_factory=dict)
    stream_callback: Optional[Callable] = None
    extra: Dict[str, Any] = field(default_factory=dict)  # For agent-specific data

    def to_dict(self) -> Dict[str, Any]:
        """Convert the context to a dictionary, removing non-serializable fields.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the context.
        """
        d = asdict(self)
        d.pop('stream_callback', None)
        return d

@dataclass
class AgentResult:
    """Standardized output from all agents.
    
    This dataclass encapsulates the result, status, data, and execution metadata
    of an agent's run.
    """
    agent_role: str
    agent_name: str
    status: str  # AgentStatus value
    data: Dict[str, Any] = field(default_factory=dict)
    output_text: str = ''
    confidence: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    @property
    def success(self) -> bool:
        """Check if the agent execution was successful.
        
        Returns:
            bool: True if the status is COMPLETED, False otherwise.
        """
        return self.status == AgentStatus.COMPLETED.value

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent result.
        """
        return asdict(self)

class BaseAgent(ABC):
    """Abstract base class for all AION scientific agents.

    Every agent in the AION system must define:
    - role: A descriptive role name (e.g., 'Literature Scout')
    - objective: What this agent aims to accomplish
    - system_prompt: The LLM system prompt for this agent's behavior

    Agents implement execute() which receives an AgentContext and returns an AgentResult.
    The base class provides:
    - Automatic timing and error handling
    - Retry logic with configurable attempts
    - Status tracking
    - Structured logging
    - Graceful error recovery
    """

    def __init__(self):
        """Initialize the base agent with default status and metadata."""
        self._status: AgentStatus = AgentStatus.PENDING
        self._last_error: Optional[str] = None
        self._execution_count: int = 0
        self._total_execution_time: float = 0.0
        self._agent_id: str = str(uuid.uuid4())[:8]

    @property
    @abstractmethod
    def role(self) -> str:
        """The agent's role in the research process."""
        ...

    @property
    @abstractmethod
    def objective(self) -> str:
        """What this agent aims to accomplish."""
        ...

    @property
    def system_prompt(self) -> str:
        """The LLM system prompt for this agent. Override in subclass.
        
        Returns:
            str: The system prompt describing the agent's role and objective.
        """
        return f'You are a scientific research agent with the role: {self.role}. Your objective: {self.objective}'

    @property
    def tools(self) -> List[str]:
        """List of tool names this agent can use. Override in subclass.
        
        Returns:
            List[str]: A list of tool names available to this agent.
        """
        return []

    @property
    def status(self) -> AgentStatus:
        """Current execution status of the agent.
        
        Returns:
            AgentStatus: The current status of the agent.
        """
        return self._status

    @property
    def agent_id(self) -> str:
        """Unique identifier for this agent instance.
        
        Returns:
            str: The agent's unique ID.
        """
        return self._agent_id

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's primary task.

        Args:
            context: Standardized input context containing all research data

        Returns:
            AgentResult with the agent's output, status, and metadata
        """
        ...

    def run_safe(self, context: AgentContext, max_retries: int = 2, retry_delay: float = 1.0) -> AgentResult:
        """Execute with automatic error handling, timing, and retry logic.

        This is the primary entry point for the orchestrator to call agents.
        It wraps execute() with:
        - Automatic timing measurement
        - Exception catching and structured error reporting
        - Configurable retry logic with exponential backoff
        - Status transitions (PENDING -> RUNNING -> COMPLETED/FAILED)
        - Structured logging
        
        Args:
            context (AgentContext): The input context for the execution.
            max_retries (int): Maximum number of retry attempts upon failure.
            retry_delay (float): Initial delay between retries in seconds.

        Returns:
            AgentResult: The result of the execution.
        """
        last_error = None
        for attempt in range(max_retries + 1):
            self._status = AgentStatus.RETRYING if attempt > 0 else AgentStatus.RUNNING
            start_time = time.time()

            if attempt > 0:
                logger.info(f'[{self.role}] Retry attempt {attempt}/{max_retries}')
                time.sleep(retry_delay * (2 ** (attempt - 1)))  # Exponential backoff

            try:
                logger.info(f'[{self.role}] Starting execution (attempt {attempt + 1})')
                result = self.execute(context)
                elapsed = time.time() - start_time
                result.execution_time_seconds = elapsed
                self._status = AgentStatus.COMPLETED
                self._execution_count += 1
                self._total_execution_time += elapsed
                logger.info(f'[{self.role}] Completed in {elapsed:.2f}s')
                return result

            except Exception as e:
                elapsed = time.time() - start_time
                last_error = str(e)
                self._last_error = last_error
                logger.error(f'[{self.role}] Error on attempt {attempt + 1}: {last_error}')
                logger.debug(traceback.format_exc())

        # All retries exhausted
        self._status = AgentStatus.FAILED
        logger.error(f'[{self.role}] All {max_retries + 1} attempts failed')
        return AgentResult(
            agent_role=self.role,
            agent_name=self.__class__.__name__,
            status=AgentStatus.FAILED.value,
            errors=[last_error or 'Unknown error after all retries'],
            execution_time_seconds=time.time() - start_time if 'start_time' in dir() else 0.0,
            confidence=0.0
        )

    def handle_error(self, error: Exception, context: AgentContext) -> AgentResult:
        """Create a structured error result. Can be overridden for custom error handling.
        
        Args:
            error (Exception): The exception that occurred.
            context (AgentContext): The context at the time of the error.
            
        Returns:
            AgentResult: A standardized error result.
        """
        return AgentResult(
            agent_role=self.role,
            agent_name=self.__class__.__name__,
            status=AgentStatus.FAILED.value,
            errors=[str(error), traceback.format_exc()],
            confidence=0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent state for persistence.
        
        Returns:
            Dict[str, Any]: A dictionary containing the agent's serialized state.
        """
        return {
            'agent_id': self._agent_id,
            'role': self.role,
            'objective': self.objective,
            'status': self._status.value,
            'class_name': self.__class__.__name__,
            'execution_count': self._execution_count,
            'total_execution_time': self._total_execution_time,
            'last_error': self._last_error
        }

    def __repr__(self) -> str:
        """Return a string representation of the agent."""
        return f'<{self.__class__.__name__} role="{self.role}" status={self._status.value}>'
