from typing import List, Dict, Any, Optional
from engines.explainability_engine import ExplainabilityEngine
from database.models import ExplainabilityReport, NoveltyScores

class ExplainabilityAgent:
    """
    Agent responsible for generating human-readable explainability reports ("Why AION Selected This Hypothesis").
    """
    def __init__(self):
        self.engine = ExplainabilityEngine()

    def run(
        self,
        research_id: str,
        hypothesis_title: str,
        hypothesis_content: str,
        scores: NoveltyScores,
        gaps: List[Any],
        papers: List[Dict[str, Any]],
        past_hypotheses: Optional[List[str]] = None,
        cross_domain_info: Optional[Dict[str, Any]] = None
    ) -> ExplainabilityReport:
        print("[ExplainabilityAgent] Compiling decision rationale explanation report...")
        return self.engine.generate_report(
            research_id, hypothesis_title, hypothesis_content, scores, gaps, papers, past_hypotheses, cross_domain_info
        )
