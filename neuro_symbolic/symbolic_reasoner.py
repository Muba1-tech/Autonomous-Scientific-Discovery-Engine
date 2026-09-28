from neuro_symbolic.rule_engine import RuleEngine
from database.db_manager import DBManager

class SymbolicReasoner:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.db = DBManager()
        
    def reason(self, hypothesis: str, risk_score: float) -> dict:
        # Self-Evolve: Adapt rule strictness based on historical success
        success_rate = self.db.get_success_rate()
        self.rule_engine.adapt(success_rate)
        
        context = {
            "hypothesis": hypothesis,
            "risk_score": risk_score
        }
        is_valid = self.rule_engine.evaluate(context)
        return {
            "hypothesis": hypothesis,
            "symbolic_validity": is_valid,
            "reasoning": "Passed all symbolic logic rules." if is_valid else "Failed rule constraints."
        }
