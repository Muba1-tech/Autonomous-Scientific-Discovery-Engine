"""
AION X 2.0 — Autonomous Scientific Research Director
Executive scientific orchestration layer that dynamically decides:
- Which specialized agent runs next
- Which hypothesis receives computational resources
- Whether additional literature retrieval is required
- Whether evidence is sufficient to justify experiments
- Whether a hypothesis should be falsified/killed or evolved
- When research should branch or terminate (stopping criteria)
- Research budget and uncertainty-aware decision making
"""

import uuid
import time
import logging
from typing import Dict, Any, List, Optional

from database.models import MissionStatus
from database.db_manager import DBManager
from core.research_tree import ResearchTree
from core.research_budget import ResearchBudgetManager

logger = logging.getLogger(__name__)


class ResearchDirector:
    """
    Intelligent Scientific Director for AION X 2.0.
    Dynamically routes agents and manages hypothesis survival based on empirical evidence.
    """

    def __init__(self, mission_id: Optional[str] = None, max_budget_usd: float = 10.0, db_manager: Optional[DBManager] = None):
        self.mission_id = mission_id or f"MIS-{uuid.uuid4().hex[:6].upper()}"
        self.db = db_manager
        self.tree = ResearchTree(self.mission_id, db_manager=db_manager)
        self.budget = ResearchBudgetManager(max_budget_usd=max_budget_usd)
        self.current_state = MissionStatus.PLANNING.value
        self.active_hypotheses: List[Dict[str, Any]] = []
        self.killed_hypotheses: List[Dict[str, Any]] = []
        self.completed_experiments: List[Dict[str, Any]] = []
        self.decision_logs: List[str] = []

    def decide_next_step(self, current_phase: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically evaluates current research state and decides the next optimal action.
        """
        papers = context.get('papers', [])
        gaps = context.get('gaps', [])
        hypotheses = context.get('hypotheses', [])
        scores = context.get('scores', {})
        falsification = context.get('falsification', {})
        experiment = context.get('experiment', {})

        decision = {
            "current_phase": current_phase,
            "next_action": "PROCEED",
            "recommended_agent": "None",
            "reasoning": "",
            "should_branch": False,
            "should_stop": False
        }

        # 1. Literature sufficiency check
        if current_phase == "LITERATURE_DISCOVERY":
            if len(papers) < 3:
                decision["next_action"] = "EXPAND_LITERATURE_SEARCH"
                decision["recommended_agent"] = "ResearcherAgent"
                decision["reasoning"] = "Indexed literature is sparse (<3 papers). Querying cross-disciplinary databases."
            else:
                decision["next_action"] = "PROCEED_TO_GAP_DETECTION"
                decision["recommended_agent"] = "GapAgent"
                decision["reasoning"] = f"Sufficient literature indexed ({len(papers)} papers). Proceeding to extract research gaps."

        # 2. Hypothesis evaluation and branching check
        elif current_phase == "HYPOTHESIS_GENERATION":
            if not hypotheses:
                decision["next_action"] = "RETRY_HYPOTHESIS_SYNTHESIS"
                decision["recommended_agent"] = "InnovatorAgent"
                decision["reasoning"] = "No candidate hypotheses generated. Re-running first-principles derivation."
            else:
                decision["next_action"] = "ENTER_EVOLUTIONARY_SEARCH"
                decision["recommended_agent"] = "CrossDomainAgent"
                decision["should_branch"] = True
                decision["reasoning"] = f"Synthesized {len(hypotheses)} seed hypotheses. Branching into genetic evolution."

        # 3. Kill Chain & Falsification check
        elif current_phase == "FALSIFYING":
            survival = falsification.get('survival_score', 80.0)
            if survival < 50.0:
                decision["next_action"] = "KILL_HYPOTHESIS"
                decision["recommended_agent"] = "FailureVault"
                decision["reasoning"] = f"Hypothesis resilience {survival}% is below critical threshold (50%). Terminating branch."
            else:
                decision["next_action"] = "PROCEED_TO_EXPERIMENTATION"
                decision["recommended_agent"] = "ExperimentAgent"
                decision["reasoning"] = f"Hypothesis demonstrated empirical resilience ({survival}%). Cleared for sandboxed experimentation."

        # 4. Stopping Criteria / Budget Check
        if self.budget.usage.is_exhausted:
            decision["should_stop"] = True
            decision["reasoning"] += " [Budget limit reached; halting active exploration]"

        self.decision_logs.append(f"[{current_phase}] -> {decision['next_action']}: {decision['reasoning']}")
        return decision

    def log_decision(self, message: str):
        self.decision_logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")
