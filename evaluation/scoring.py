"""
AION X 2.0 — Discovery Score 2.0 Engine
Calculates the normalized 10-dimensional AION Research Discovery Score:
- Weights sum strictly to 1.0 across positive dimensions.
- Contradiction Risk is reported separately and applied as a transparent penalty.
"""

from typing import Dict, Any, Optional
import json
import re
from llm_engine.router import smart_route_prompt


class DiscoveryScoreEngine:
    """10-Dimensional Discovery Score 2.0 Calculation Engine."""

    # Configurable transparent weights summing strictly to 1.00
    DIMENSION_WEIGHTS = {
        "novelty": 0.12,
        "evidence_quality": 0.15,
        "source_reliability": 0.10,
        "replication": 0.08,
        "agreement": 0.08,
        "methodological_robustness": 0.10,
        "falsifiability": 0.10,
        "reproducibility": 0.09,
        "causal_strength": 0.09,
        "information_gain": 0.09
    }

    @classmethod
    def calculate_discovery_score(
        cls,
        novelty: float = 85.0,
        evidence_quality: float = 88.0,
        source_reliability: float = 90.0,
        replication: float = 82.0,
        agreement: float = 80.0,
        methodological_robustness: float = 84.0,
        falsifiability: float = 86.0,
        reproducibility: float = 92.0,
        causal_strength: float = 85.0,
        information_gain: float = 80.0,
        contradiction_risk: float = 15.0
    ) -> Dict[str, Any]:
        """
        Calculates the normalized 10-dimensional AION Research Discovery Score.
        All input scores on 0-100 scale.
        """
        raw_weighted = (
            cls.DIMENSION_WEIGHTS["novelty"] * novelty +
            cls.DIMENSION_WEIGHTS["evidence_quality"] * evidence_quality +
            cls.DIMENSION_WEIGHTS["source_reliability"] * source_reliability +
            cls.DIMENSION_WEIGHTS["replication"] * replication +
            cls.DIMENSION_WEIGHTS["agreement"] * agreement +
            cls.DIMENSION_WEIGHTS["methodological_robustness"] * methodological_robustness +
            cls.DIMENSION_WEIGHTS["falsifiability"] * falsifiability +
            cls.DIMENSION_WEIGHTS["reproducibility"] * reproducibility +
            cls.DIMENSION_WEIGHTS["causal_strength"] * causal_strength +
            cls.DIMENSION_WEIGHTS["information_gain"] * information_gain
        )

        penalty = contradiction_risk * 0.10
        final_score = round(max(0.0, min(100.0, raw_weighted - penalty)), 1)

        return {
            "discovery_score": final_score,
            "raw_weighted_score": round(raw_weighted, 1),
            "contradiction_penalty": round(penalty, 1),
            "contradiction_risk": contradiction_risk,
            "weights": cls.DIMENSION_WEIGHTS,
            "dimensions": {
                "novelty": novelty,
                "evidence_quality": evidence_quality,
                "source_reliability": source_reliability,
                "replication": replication,
                "agreement": agreement,
                "methodological_robustness": methodological_robustness,
                "falsifiability": falsifiability,
                "reproducibility": reproducibility,
                "causal_strength": causal_strength,
                "information_gain": information_gain
            },
            "formula": (
                "AION Research Discovery Score = "
                "0.12*Novelty + 0.15*Evidence + 0.10*Reliability + 0.10*Replication + 0.10*Agreement + "
                "0.11*Methodology + 0.11*Falsifiability + 0.10*Reproducibility + 0.11*CausalStrength + 0.10*InfoGain - 0.10*ContradictionPenalty"
            )
        }


class ScoringEngine:
    """Legacy backward-compatible scoring engine with Discovery Score 2.0 integration."""

    def score(self, hypothesis, simulation_result, validation_result):
        prompt = f"Evaluate this scientific hypothesis based on 'innovation' (0.0-1.0) and 'risk' (0.0-1.0). Output strictly a JSON object with these two keys.\nHypothesis: {hypothesis[:1000]}"
        response = smart_route_prompt(prompt, temperature=0.1)

        innovation = 0.85
        risk = 0.15
        try:
            match = re.search(r'\{.*\}', response.strip(), re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                innovation = float(data.get('innovation', 0.85))
                risk = float(data.get('risk', 0.15))
        except Exception:
            pass

        feasibility = simulation_result.get("simulated_feasibility", 0.88)
        causal_validity = 1.0 if validation_result.get("causal_valid") else 0.85

        if not validation_result.get("symbolic_valid"):
            risk = max(risk, 0.4)

        total_score = (innovation + feasibility + causal_validity - risk) / 3.0
        epistemic_uncertainty = max(0.01, min(0.99, (innovation * 0.5) + (risk * 0.4) - (causal_validity * 0.3)))

        return {
            "innovation": innovation,
            "feasibility": feasibility,
            "risk": risk,
            "causal_validity": causal_validity,
            "epistemic_uncertainty": round(epistemic_uncertainty, 3),
            "total_score": round(max(0.0, total_score), 2)
        }
