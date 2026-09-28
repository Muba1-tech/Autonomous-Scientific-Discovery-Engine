from typing import Tuple, List, Dict, Any
from engines.self_correction_engine import SelfCorrectionEngine

class SelfCorrectionAgent:
    """
    Agent responsible for running 5-layer sanity validation and auto-correcting hypotheses.
    """
    def __init__(self):
        self.engine = SelfCorrectionEngine()

    def run(self, hypothesis: str, context: str) -> Tuple[str, List[Dict[str, Any]]]:
        print("[SelfCorrectionAgent] Running 5-layer validation loop & self-correction...")
        return self.engine.self_correct(hypothesis, context)
