from typing import List, Dict, Any
from engines.research_gap_detector import ResearchGapDetector
from database.models import ResearchGap

class GapAgent:
    """
    Dedicated agent for identifying, categorizing, and scoring research gaps.
    """
    def __init__(self):
        self.detector = ResearchGapDetector()

    def run(self, papers: List[Dict[str, Any]], domain: str, research_id: str = "GAP_SESSION") -> List[ResearchGap]:
        print("[GapAgent] Ingesting papers and detecting research gaps...")
        return self.detector.detect_gaps(papers, domain, research_id)
