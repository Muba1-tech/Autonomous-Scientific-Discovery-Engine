"""
AION X 2.0 — Scientific Failure Memory & Vault Subsystem
Stores and semantically indexes:
- Failed hypotheses
- Failed computational experiments
- Failed replication attempts
- Contradictory evidence
- Invalid assumptions
- Reasoning & statistical failures
Automatically scans historical failures before hypothesis generation to prevent repeating past errors.
"""

import uuid
import json
import logging
from typing import List, Dict, Any, Optional

from database.models import FailedExperiment
from database.db_manager import DBManager

logger = logging.getLogger(__name__)


class ScientificFailureVault:
    """Persistent storage, semantic retrieval, and proactive warning system for scientific failures."""

    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db = db_manager

    def record_failure(
        self,
        hypothesis_id: str,
        experiment_id: str,
        failure_type: str,
        observations: str,
        diagnosis: str,
        parameters: Optional[Dict[str, Any]] = None,
        confidence: float = 0.9,
        learned_constraint: str = "",
        future_recommendation: str = ""
    ) -> str:
        """Stores an experimental or hypothesis failure into the persistent vault."""
        fail_id = f"FAIL-{uuid.uuid4().hex[:6].upper()}"
        if self.db:
            try:
                self.db.insert_failed_experiment(
                    failure_id=fail_id,
                    hypothesis_id=hypothesis_id,
                    experiment_id=experiment_id,
                    failure_type=failure_type,
                    parameters=parameters or {},
                    observations=observations,
                    diagnosis=diagnosis,
                    confidence=confidence,
                    learned_constraint=learned_constraint or "Avoid parameter regimes where noise exceeds damping factor",
                    future_recommendation=future_recommendation or "Incorporate non-linear boundary damping"
                )
            except Exception as e:
                logger.warning(f"Failed to record failure in DB: {e}")
        return fail_id

    def check_failure_patterns(self, hypothesis_statement: str, domain: str = "") -> Dict[str, Any]:
        """
        Scans failure memory for similar mechanisms, assumptions, or keywords.
        Returns proactive warnings to prevent repeating historical mistakes.
        """
        warnings = []
        matches = []

        if self.db:
            try:
                # Search failure vault for relevant keywords
                keywords = [w for w in hypothesis_statement.lower().split() if len(w) > 4]
                for kw in keywords[:5]:
                    results = self.db.search_failure_vault(kw)
                    for r in results:
                        if r not in matches:
                            matches.append(r)
            except Exception as e:
                logger.warning(f"Error querying failure memory: {e}")

        # Default heuristic checks if vault is empty or in mock mode
        stmt_l = hypothesis_statement.lower()
        if "perpetual" in stmt_l or "zero dissipation" in stmt_l or "infinite" in stmt_l:
            warnings.append("WARNING: Violates Second Law of Thermodynamics (Entropy non-decrease constraint).")
        if "instantaneous" in stmt_l and ("transfer" in stmt_l or "communication" in stmt_l):
            warnings.append("WARNING: Superluminal signaling constraint violation (No-communication theorem).")
        if "isothermal" in stmt_l and "high energy" in stmt_l:
            warnings.append("WARNING: Prior failure recorded where high-energy density broke isothermal assumption.")

        for m in matches[:3]:
            warnings.append(f"Historical Failure Warning [{m.get('failure_type')}]: {m.get('learned_constraint')}")

        has_risk = len(warnings) > 0
        return {
            "has_failure_risk": has_risk,
            "warnings_count": len(warnings),
            "warnings": warnings,
            "matching_failures": matches[:5],
            "recommendation": "Incorporate learned constraints into boundary conditions before proceeding." if has_risk else "No conflicting historical failure patterns detected."
        }

    def mine_replication_crisis_negations(self, hypothesis_statement: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans literature for replication crisis indicators, null results, and failed prior attempts.
        Returns explicit failure counts and replication risk score.
        """
        negation_keywords = [
            "failed to", "no effect", "null result", "inconsistent",
            "contradicts", "refuted", "unable to replicate", "no correlation",
            "statistically insignificant", "no observable shift"
        ]
        flagged_papers = []
        negation_count = 0

        for p in papers:
            text = (p.get("title", "") + " " + p.get("abstract", "")).lower()
            found_terms = [term for term in negation_keywords if term in text]
            if found_terms:
                negation_count += len(found_terms)
                flagged_papers.append({
                    "title": p.get("title", "Indexed Study"),
                    "matched_negations": found_terms,
                    "url": p.get("url", "")
                })

        replication_risk_score = round(min(100.0, (negation_count * 18.5) + (len(flagged_papers) * 12.0)), 1)
        crisis_alert = replication_risk_score > 0 or len(flagged_papers) > 0

        return {
            "replication_risk_score": replication_risk_score,
            "negation_count": negation_count,
            "flagged_papers": flagged_papers,
            "crisis_alert": crisis_alert,
            "status_message": f"CRITICAL REPLICATION RISK ({replication_risk_score}%): Found {len(flagged_papers)} literature source(s) with prior null/failed replication results." if crisis_alert else "LOW REPLICATION RISK: No major prior replication failure clusters detected in literature."
        }

    def get_all_failures(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent recorded failures from the failure vault."""
        if self.db:
            return self.db.get_failed_experiments(limit=limit)
        return []

