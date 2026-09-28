from typing import Optional
from engines.cross_domain_engine import CrossDomainEngine
from database.models import CrossDomainHypothesis

class CrossDomainAgent:
    """
    Agent responsible for cross-domain knowledge discovery and concept transfer.
    """
    def __init__(self):
        self.engine = CrossDomainEngine()

    def run(self, source_domain: str, target_domain: str, context: Optional[str] = "") -> CrossDomainHypothesis:
        print(f"[CrossDomainAgent] Synthesizing cross-domain transfer from {source_domain} -> {target_domain}...")
        return self.engine.generate_cross_domain_hypothesis(source_domain, target_domain, context)
