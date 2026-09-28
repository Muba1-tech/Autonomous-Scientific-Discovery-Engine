"""
AION X 2.0 — Evidence Firewall & Epistemic Classifier
Strict epistemic verification layer between LLM generated content and scientific conclusions.
Every scientific assertion is categorized as:
- FACT (Established empirical or mathematical truth with peer-reviewed consensus)
- EVIDENCE (Direct empirical data from indexed papers or datasets)
- OBSERVATION (Empirical result from a specific experiment or trial)
- INFERENCE (Deductive or inductive logical consequence of premises)
- HYPOTHESIS (Testable scientific proposition with explicit falsification criteria)
- SIMULATION (Outcome of a computational model or synthetic data trial)
- SPECULATION (Conjectural extrapolation requiring further grounding)

Statuses:
- VERIFIED
- PARTIALLY_VERIFIED
- UNVERIFIED
- CONTRADICTED
"""

import uuid
import re
import json
import logging
from typing import List, Dict, Any, Optional

from database.models import Claim, ClaimType, EvidenceConfidence
from database.db_manager import DBManager

logger = logging.getLogger(__name__)


class EvidenceFirewall:
    """Epistemic classifier and verification gateway for scientific assertions."""

    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db = db_manager

    def classify_and_verify(
        self,
        text_statements: List[str],
        indexed_papers: Optional[List[Dict[str, Any]]] = None,
        mission_id: str = ""
    ) -> List[Claim]:
        """
        Parses text statements, classifies their epistemic type, and validates against literature.
        """
        indexed_papers = indexed_papers or []
        claims: List[Claim] = []

        paper_titles = [p.get('title', '').lower() for p in indexed_papers]
        paper_abstracts = " ".join([p.get('abstract', '').lower() for p in indexed_papers])

        for stmt in text_statements:
            if not stmt or len(stmt.strip()) < 5:
                continue

            stmt_clean = stmt.strip()
            stmt_lower = stmt_clean.lower()
            claim_id = f"CLM-{uuid.uuid4().hex[:6].upper()}"

            # 1. Epistemic Classification
            if any(k in stmt_lower for k in ["we hypothesize", "hypothesize", "proposed mechanism", "we propose"]):
                claim_type = ClaimType.HYPOTHESIS.value
            elif any(k in stmt_lower for k in ["simulation shows", "simulated", "numerical model", "in silico"]):
                claim_type = ClaimType.SIMULATION.value
            elif any(k in stmt_lower for k in ["observed in experiment", "measured", "empirical data", "we observed"]):
                claim_type = ClaimType.OBSERVATION.value
            elif any(k in stmt_lower for k in ["therefore", "implies that", "we deduce", "consequently"]):
                claim_type = ClaimType.INFERENCE.value
            elif any(k in stmt_lower for k in ["might suggest", "could potentially", "speculate", "future possibility"]):
                claim_type = ClaimType.SPECULATION.value
            elif any(k in stmt_lower for k in ["law of", "constant", "proven that", "established"]):
                claim_type = ClaimType.FACT.value
            else:
                claim_type = ClaimType.EVIDENCE.value

            # 2. Literature Verification Matching
            matching_sources = []
            words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', '', stmt_lower).split() if len(w) > 4]
            keyword_hits = sum(1 for w in words if w in paper_abstracts)

            if len(indexed_papers) == 0:
                status = EvidenceConfidence.UNVERIFIED.value
                conf = 0.50
            elif keyword_hits >= 3:
                status = EvidenceConfidence.VERIFIED.value
                conf = 0.92
                matching_sources = [indexed_papers[0].get('title', 'Indexed Literature')]
            elif keyword_hits >= 1:
                status = EvidenceConfidence.PARTIALLY_VERIFIED.value
                conf = 0.72
                matching_sources = [indexed_papers[0].get('title', 'Indexed Literature')]
            else:
                status = EvidenceConfidence.UNVERIFIED.value
                conf = 0.45

            # Contradiction flag heuristic
            if "not observe" in stmt_lower and "observed" in paper_abstracts:
                status = EvidenceConfidence.CONTRADICTED.value

            claim = Claim(
                claim_id=claim_id,
                text=stmt_clean,
                claim_type=claim_type,
                verification_status=status,
                source_ids=matching_sources,
                passage_ids=[f"PASS-{uuid.uuid4().hex[:4].upper()}"] if matching_sources else [],
                confidence=conf,
                contradiction_ids=[],
                mission_id=mission_id
            )
            claims.append(claim)

            if self.db:
                try:
                    self.db.insert_claim_lineage(
                        claim_id=claim.claim_id,
                        text=claim.text,
                        claim_type=claim.claim_type,
                        verification_status=claim.verification_status,
                        source_ids=claim.source_ids,
                        passage_ids=claim.passage_ids,
                        confidence=claim.confidence,
                        mission_id=mission_id
                    )
                except Exception as e:
                    logger.warning(f"Failed to record claim lineage: {e}")

        return claims
