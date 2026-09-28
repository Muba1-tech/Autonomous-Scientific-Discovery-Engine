"""
AION X 2.0 — Research Budget & Cost Management
Tracks and enforces computational budgets:
- LLM prompt & completion tokens
- Embedding calculations
- External literature retrieval calls
- Sandbox experiment executions
- Database read/write operations
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class BudgetUsage:
    """Detailed research budget consumption metrics."""
    max_budget_usd: float = 10.0
    current_cost_usd: float = 0.0
    llm_calls: int = 0
    total_tokens: int = 0
    embedding_calls: int = 0
    retrieval_queries: int = 0
    experiments_executed: int = 0
    simulations_executed: int = 0
    is_exhausted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResearchBudgetManager:
    """Tracks and caps resource expenditure during autonomous discovery."""

    def __init__(self, max_budget_usd: float = 10.0):
        self.usage = BudgetUsage(max_budget_usd=max_budget_usd)

    def record_llm_call(self, prompt_tokens: int = 150, completion_tokens: int = 250, cost_per_1k: float = 0.0015):
        """Records LLM token expenditure."""
        self.usage.llm_calls += 1
        self.usage.total_tokens += (prompt_tokens + completion_tokens)
        cost = ((prompt_tokens + completion_tokens) / 1000.0) * cost_per_1k
        self.usage.current_cost_usd += round(cost, 5)
        self._check_exhaustion()

    def record_retrieval(self, query_count: int = 1):
        """Records literature retrieval query."""
        self.usage.retrieval_queries += query_count
        self.usage.current_cost_usd += round(0.0005 * query_count, 5)
        self._check_exhaustion()

    def record_experiment(self, is_simulation: bool = False):
        """Records sandboxed execution cost."""
        if is_simulation:
            self.usage.simulations_executed += 1
            self.usage.current_cost_usd += 0.002
        else:
            self.usage.experiments_executed += 1
            self.usage.current_cost_usd += 0.005
        self._check_exhaustion()

    def _check_exhaustion(self):
        if self.usage.current_cost_usd >= self.usage.max_budget_usd:
            self.usage.is_exhausted = True
            logger.warning(f"Research Budget Exhausted: ${self.usage.current_cost_usd:.4f} / ${self.usage.max_budget_usd:.2f}")

    def get_status(self) -> Dict[str, Any]:
        percent = (self.usage.current_cost_usd / self.usage.max_budget_usd) * 100.0 if self.usage.max_budget_usd > 0 else 0.0
        return {
            "max_budget_usd": self.usage.max_budget_usd,
            "current_cost_usd": round(self.usage.current_cost_usd, 4),
            "budget_used_percent": round(min(100.0, percent), 1),
            "llm_calls": self.usage.llm_calls,
            "total_tokens": self.usage.total_tokens,
            "experiments_executed": self.usage.experiments_executed,
            "is_exhausted": self.usage.is_exhausted
        }
