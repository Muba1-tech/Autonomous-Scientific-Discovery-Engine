from typing import List, Dict, Any
from engines.citation_verifier import CitationVerifier
from database.models import VerificationResult

class CitationAgent:
    """
    Agent responsible for verifying factual claims and enforcing the Hallucination Firewall.
    """
    def __init__(self):
        self.verifier = CitationVerifier()

    def run(self, text: str, papers: List[Dict[str, Any]]) -> VerificationResult:
        print("[CitationAgent] Verifying factual claims against retrieved evidence...")
        return self.verifier.verify_claims(text, papers)
