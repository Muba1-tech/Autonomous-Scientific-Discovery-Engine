from typing import List, Dict, Any, Optional
from engines.evolutionary_memory import EvolutionaryMemoryEngine
from database.db_manager import DBManager

class MemoryAgent:
    """
    Agent responsible for learning from past research attempts and feeding evolutionary insights forward.
    """
    def __init__(self, db: Optional[DBManager] = None):
        self.engine = EvolutionaryMemoryEngine(db)

    def record(self, research_id: str, domain: str, hypothesis: str, evidence: str, methodology: str, result: str, outcome: str = "SUCCESS", score: float = 0.0):
        print(f"[MemoryAgent] Storing research outcome in Evolutionary Memory...")
        self.engine.record_cycle(
            research_id=research_id,
            domain=domain,
            hypothesis=hypothesis,
            evidence=evidence,
            methodology=methodology,
            experiment_result=result,
            outcome=outcome,
            novelty_score=score,
            feasibility_score=score,
            impact_score=score
        )

    def get_context(self, domain: str) -> str:
        return self.engine.get_evolutionary_prompt_context(domain)
