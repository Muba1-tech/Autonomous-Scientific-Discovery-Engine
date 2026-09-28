import logging
from dataclasses import dataclass
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class ResearchGap:
    description: str
    novelty_score: float
    impact_score: float
    feasibility_score: float
    evidence_availability: float
    opportunity_score: float = 0.0

class ResearchGapAnalyzer:
    def __init__(self, novelty_weight: float = 0.3, impact_weight: float = 0.4, feasibility_weight: float = 0.2, evidence_weight: float = 0.1):
        self.weights = {
            "novelty": novelty_weight,
            "impact": impact_weight,
            "feasibility": feasibility_weight,
            "evidence": evidence_weight
        }

    def analyze(self, gaps: List[Dict[str, Any]]) -> List[ResearchGap]:
        analyzed_gaps = []
        for gap in gaps:
            desc = gap.get("description", "Unknown Gap")
            novelty = gap.get("novelty_score", 0.0)
            impact = gap.get("impact_score", 0.0)
            feasibility = gap.get("feasibility_score", 0.0)
            evidence = gap.get("evidence_availability", 0.0)

            opportunity_score = (
                novelty * self.weights["novelty"] +
                impact * self.weights["impact"] +
                feasibility * self.weights["feasibility"] +
                evidence * self.weights["evidence"]
            )

            analyzed_gaps.append(ResearchGap(
                description=desc,
                novelty_score=novelty,
                impact_score=impact,
                feasibility_score=feasibility,
                evidence_availability=evidence,
                opportunity_score=opportunity_score
            ))
        
        # Rank by opportunity score
        analyzed_gaps.sort(key=lambda x: x.opportunity_score, reverse=True)
        return analyzed_gaps
