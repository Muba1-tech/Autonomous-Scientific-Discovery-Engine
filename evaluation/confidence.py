"""AION Discovery Index & Multi-Dimensional Scientific Confidence System.
Transparently evaluates hypotheses across 10 empirical and methodological dimensions,
penalizes contradiction risk, and outputs traceable, verifiable confidence metrics.
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceMetrics:
    overall_confidence: float = 0.0
    novelty_score: float = 0.0
    impact_factor: float = 0.0
    evidence_quality: float = 0.0
    source_reliability: float = 0.0
    replication: float = 0.0
    agreement: float = 0.0
    contradiction_risk: float = 0.0
    methodological_robustness: float = 0.0
    falsifiability: float = 0.0
    reproducibility: float = 0.0
    novelty: float = 0.0
    uncertainty: float = 0.0
    aion_discovery_index: float = 0.0
    dimensions: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScientificConfidenceSystem:
    """Calculates transparent, multi-dimensional confidence scores and Discovery Index."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "evidence_quality": 0.15,
            "source_reliability": 0.10,
            "replication": 0.12,
            "agreement": 0.10,
            "methodological_robustness": 0.15,
            "falsifiability": 0.12,
            "reproducibility": 0.11,
            "novelty": 0.15,
            "contradiction_penalty": 0.10,
            "uncertainty_penalty": 0.05
        }

    def calculate_confidence(
        self,
        evidence_strength: float = 0.5,
        methodology_rigor: float = 0.5,
        reproducibility: float = 0.5,
        falsifiability: float = 0.5,
        novelty: float = 0.5,
        **kwargs
    ) -> ConfidenceMetrics:
        """Compute confidence metrics from individual empirical and methodological dimensions."""
        dimensions = {
            "evidence": evidence_strength,
            "methodology": methodology_rigor,
            "reproducibility": reproducibility,
            "falsifiability": falsifiability,
            "novelty": novelty
        }
        dimensions.update(kwargs)

        overall = (
            evidence_strength * 0.35 +
            methodology_rigor * 0.35 +
            reproducibility * 0.30
        )

        return ConfidenceMetrics(
            overall_confidence=round(overall, 3),
            evidence_quality=evidence_strength,
            methodological_robustness=methodology_rigor,
            reproducibility=reproducibility,
            falsifiability=falsifiability,
            novelty=novelty,
            novelty_score=novelty,
            dimensions=dimensions,
            aion_discovery_index=round(overall, 3)
        )

    def calculate_discovery_index(self, metrics: ConfidenceMetrics) -> float:
        """Calculate the composite AION Discovery Index (0.0 to 1.0).
        Formula: 0.40 * overall_confidence + 0.35 * novelty + 0.25 * impact
        """
        novelty = metrics.novelty_score if metrics.novelty_score > 0 else metrics.novelty
        impact = metrics.impact_factor if metrics.impact_factor > 0 else 0.70
        confidence = metrics.overall_confidence if metrics.overall_confidence > 0 else metrics.evidence_quality

        index = (0.40 * confidence) + (0.35 * novelty) + (0.25 * impact)
        return round(float(index), 3)

    def compute_confidence(self, data: Dict[str, float]) -> ConfidenceMetrics:
        """Backward-compatible full 10-dimension evaluation."""
        eq = data.get("evidence_quality", 0.5)
        sr = data.get("source_reliability", 0.5)
        rep = data.get("replication", 0.5)
        agr = data.get("agreement", 0.5)
        c_risk = data.get("contradiction_risk", 0.2)
        mr = data.get("methodological_robustness", 0.5)
        fal = data.get("falsifiability", 0.5)
        reprod = data.get("reproducibility", 0.5)
        nov = data.get("novelty", 0.5)
        unc = data.get("uncertainty", 0.3)

        base_score = (
            eq * self.weights.get("evidence_quality", 0.15) +
            sr * self.weights.get("source_reliability", 0.10) +
            rep * self.weights.get("replication", 0.12) +
            agr * self.weights.get("agreement", 0.10) +
            mr * self.weights.get("methodological_robustness", 0.15) +
            fal * self.weights.get("falsifiability", 0.12) +
            reprod * self.weights.get("reproducibility", 0.11) +
            nov * self.weights.get("novelty", 0.15)
        )
        penalty = (c_risk * self.weights.get("contradiction_penalty", 0.10)) + (unc * self.weights.get("uncertainty_penalty", 0.05))
        discovery_index = max(0.0, min(1.0, base_score - penalty))

        return ConfidenceMetrics(
            overall_confidence=round(base_score, 3),
            novelty_score=nov,
            impact_factor=0.80,
            evidence_quality=eq,
            source_reliability=sr,
            replication=rep,
            agreement=agr,
            contradiction_risk=c_risk,
            methodological_robustness=mr,
            falsifiability=fal,
            reproducibility=reprod,
            novelty=nov,
            uncertainty=unc,
            aion_discovery_index=round(discovery_index, 3),
            dimensions=data
        )

    def generate_transparency_report(self, metrics: ConfidenceMetrics) -> str:
        """Generate structured markdown transparency report showing all score components."""
        return (
            f"### AION Discovery Index & Confidence Transparency Report\n"
            f"- **overall_confidence**: {metrics.overall_confidence:.2f}\n"
            f"- **novelty_score**: {metrics.novelty_score:.2f}\n"
            f"- **impact_factor**: {metrics.impact_factor:.2f}\n"
            f"- **evidence_quality**: {metrics.evidence_quality:.2f}\n"
            f"- **methodological_robustness**: {metrics.methodological_robustness:.2f}\n"
            f"- **reproducibility**: {metrics.reproducibility:.2f}\n"
            f"- **contradiction_risk**: {metrics.contradiction_risk:.2f}\n"
            f"- **aion_discovery_index**: {metrics.aion_discovery_index:.2f}\n"
        )
