import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum

from llm_engine.router import smart_route_prompt

logger = logging.getLogger(__name__)

class ContradictionStrength(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class EvidenceRecord:
    source: str
    finding: str
    methodology: str
    dataset: str
    sample_size: int
    experimental_conditions: str
    supports_claim: bool

@dataclass
class ContradictionRecord:
    claim: str
    supporting_evidence: List[EvidenceRecord] = field(default_factory=list)
    contradictory_evidence: List[EvidenceRecord] = field(default_factory=list)
    strength: ContradictionStrength = ContradictionStrength.LOW
    empirical_discrepancy_hypothesis: str = ""
    methodological_differences: str = ""
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

class ContradictionHunter:
    """
    Hunts for contradictions in scientific literature for a given claim.
    """
    def __init__(self):
        pass
        
    def hunt(self, claim: str) -> ContradictionRecord:
        """
        Systematically search for both supporting and contradictory literature/evidence.
        Compare methodologies, datasets, sample sizes, and experimental conditions.
        """
        prompt = f"""
You are an expert scientific researcher. Analyze the following scientific claim:
CLAIM: {claim}

Perform a rigorous search for BOTH supporting and contradictory literature and evidence. Do not perform a confirmation-only search.
You must output a JSON object with the following structure:
{{
    "supporting_evidence": [
        {{
            "source": "Citation or source name",
            "finding": "What was found",
            "methodology": "Brief methodology",
            "dataset": "Dataset used",
            "sample_size": 100,
            "experimental_conditions": "Conditions",
            "supports_claim": true
        }}
    ],
    "contradictory_evidence": [
        {{
            "source": "Citation or source name",
            "finding": "What was found",
            "methodology": "Brief methodology",
            "dataset": "Dataset used",
            "sample_size": 100,
            "experimental_conditions": "Conditions",
            "supports_claim": false
        }}
    ],
    "strength": "LOW|MEDIUM|HIGH|CRITICAL",
    "empirical_discrepancy_hypothesis": "Hypothesis for why discrepancies exist",
    "methodological_differences": "Comparison of methodologies"
}}
Return ONLY valid JSON.
"""
        try:
            response = smart_route_prompt(prompt)
            # Basic cleanup in case LLM wraps in markdown
            if response.startswith("```json"):
                response = response[7:-3].strip()
            elif response.startswith("```"):
                response = response[3:-3].strip()
                
            data = json.loads(response)
            
            supporting = [EvidenceRecord(**ev) for ev in data.get("supporting_evidence", [])]
            contradictory = [EvidenceRecord(**ev) for ev in data.get("contradictory_evidence", [])]
            
            strength_str = data.get("strength", "LOW").upper()
            try:
                strength = ContradictionStrength[strength_str]
            except KeyError:
                strength = ContradictionStrength.LOW
                
            return ContradictionRecord(
                claim=claim,
                supporting_evidence=supporting,
                contradictory_evidence=contradictory,
                strength=strength,
                empirical_discrepancy_hypothesis=data.get("empirical_discrepancy_hypothesis", ""),
                methodological_differences=data.get("methodological_differences", "")
            )
        except Exception as e:
            logger.error(f"Error hunting contradictions for claim '{claim}': {e}")
            return ContradictionRecord(claim=claim, strength=ContradictionStrength.LOW, empirical_discrepancy_hypothesis=f"Error occurred: {str(e)}")
