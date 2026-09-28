from typing import List, Dict, Any, Optional
from engines.novelty_engine import NoveltyEngine
from database.models import NoveltyScores

class NoveltyAgent:
    """
    Dedicated agent for evaluating hypothesis novelty, feasibility, impact, and evidence strength.
    """
    def __init__(self):
        self.engine = NoveltyEngine()

    def run(
        self,
        hypothesis: str,
        papers: List[Dict[str, Any]],
        past_hypotheses: Optional[List[str]] = None,
        gaps: Optional[List[Any]] = None,
        simulated_feasibility: float = 0.5,
        weights: Optional[Dict[str, float]] = None
    ) -> NoveltyScores:
        print("[NoveltyAgent] Evaluating multi-signal novelty and research priority score...")
        return self.engine.evaluate_hypothesis(
            hypothesis, papers, past_hypotheses, gaps, simulated_feasibility, weights
        )
