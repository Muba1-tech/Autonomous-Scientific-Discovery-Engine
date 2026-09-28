from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
import datetime

@dataclass
class Paper:
    title: str
    abstract: str
    source: str
    url: Optional[str] = None
    authors: Optional[List[str]] = field(default_factory=list)
    year: Optional[int] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ResearchGap:
    gap_id: str
    topic: str
    description: str
    supporting_papers: List[str]
    evidence: List[str]
    paper_count: int
    confidence_score: float
    potential_direction: str
    related_concepts: List[str]
    research_domain: str
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class NoveltyScores:
    novelty_score: float         # 0 - 100
    feasibility_score: float     # 0 - 100
    potential_impact_score: float# 0 - 100
    evidence_strength: float     # 0 - 100
    priority_score: float        # Weighted combination 0 - 100
    sub_metrics: Optional[Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ClaimVerification:
    claim_text: str
    status: str # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED, UNVERIFIED
    supporting_source: str
    relevant_evidence: str
    confidence: float
    source_url: Optional[str] = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VerificationResult:
    claims: List[ClaimVerification]
    overall_status: str
    supported_count: int
    unverified_count: int
    contradicted_count: int
    firewall_passed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SimulationResult:
    hypothesis_id: str
    simulated_feasibility: float # 0.0 to 1.0
    expected_outcome: str
    synthetic_dataset_summary: str
    evaluation_metrics: Dict[str, float]
    sandbox_log: str
    plots_base64: List[str] = field(default_factory=list)
    limitations: str = ""
    interpretation: str = ""
    csv_data: str = ""
    python_code: str = ""
    pid: Optional[int] = None
    termination_status: str = ""
    dataset_name: str = ""
    dataset_description: str = ""
    dataset_schema: Dict[str, str] = field(default_factory=dict)
    dataset_preview: List[Dict[str, Any]] = field(default_factory=list)
    expected_output_dict: Dict[str, Any] = field(default_factory=dict)
    observed_output_dict: Dict[str, Any] = field(default_factory=dict)
    ast_audit_passed: bool = True
    ast_violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CrossDomainHypothesis:
    source_domain: str
    target_domain: str
    transferred_concept: str
    transfer_rationale: str
    hypothesis_statement: str
    existing_evidence: str
    novelty_score: float
    potential_impact: float
    risks: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Hypothesis:
    research_id: str
    domain: str
    title: str
    content: str
    verdict: str
    novelty_scores: Optional[NoveltyScores] = None
    gaps_addressed: Optional[List[str]] = field(default_factory=list)
    first_principles_derivation: Optional[str] = ""
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.novelty_scores:
            d["novelty_scores"] = self.novelty_scores.to_dict()
        return d

@dataclass
class ExplainabilityReport:
    research_id: str
    selected_hypothesis_title: str
    selection_rationale: str
    gaps_involved: List[str]
    supporting_papers: List[str]
    key_evidence: List[str]
    novel_concepts: List[str]
    cross_domain_connections: List[str]
    scores_breakdown: Dict[str, float]
    previous_related_hypotheses: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ResearchSession:
    research_id: str
    domain_goal: str
    research_goal: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    status: str = "COMPLETED"
    paper_count: int = 0
    gap_count: int = 0
    hypothesis_count: int = 0
    overall_priority_score: float = 0.0


# ============================================================================
# PROJECT AION — Advanced Autonomous Scientist Upgrade Models
# ============================================================================

import enum


class MissionStatus(enum.Enum):
    """States for a research mission lifecycle."""
    PENDING = 'PENDING'
    PLANNING = 'PLANNING'
    RESEARCHING = 'RESEARCHING'
    GENERATING_HYPOTHESES = 'GENERATING_HYPOTHESES'
    EVOLVING_HYPOTHESES = 'EVOLVING_HYPOTHESES'
    FALSIFYING = 'FALSIFYING'
    EXPERIMENTING = 'EXPERIMENTING'
    PEER_REVIEW = 'PEER_REVIEW'
    SYNTHESIS = 'SYNTHESIS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    PAUSED = 'PAUSED'

    @classmethod
    def valid_transitions(cls) -> Dict[str, List[str]]:
        """Returns valid state transitions for the mission state machine."""
        return {
            cls.PENDING.value: [cls.PLANNING.value, cls.CANCELLED.value] if hasattr(cls, 'CANCELLED') else [cls.PLANNING.value, cls.FAILED.value],
            cls.PLANNING.value: [cls.RESEARCHING.value, cls.PAUSED.value, cls.FAILED.value],
            cls.RESEARCHING.value: [cls.GENERATING_HYPOTHESES.value, cls.PAUSED.value, cls.FAILED.value],
            cls.GENERATING_HYPOTHESES.value: [cls.EVOLVING_HYPOTHESES.value, cls.FALSIFYING.value, cls.PAUSED.value, cls.FAILED.value],
            cls.EVOLVING_HYPOTHESES.value: [cls.FALSIFYING.value, cls.PAUSED.value, cls.FAILED.value],
            cls.FALSIFYING.value: [cls.EXPERIMENTING.value, cls.PAUSED.value, cls.FAILED.value],
            cls.EXPERIMENTING.value: [cls.PEER_REVIEW.value, cls.PAUSED.value, cls.FAILED.value],
            cls.PEER_REVIEW.value: [cls.SYNTHESIS.value, cls.PAUSED.value, cls.FAILED.value],
            cls.SYNTHESIS.value: [cls.COMPLETED.value, cls.FAILED.value],
            cls.COMPLETED.value: [],
            cls.FAILED.value: [cls.PENDING.value],  # Retry from failed
            cls.PAUSED.value: [cls.PLANNING.value, cls.RESEARCHING.value, cls.GENERATING_HYPOTHESES.value,
                               cls.EVOLVING_HYPOTHESES.value, cls.FALSIFYING.value, cls.EXPERIMENTING.value,
                               cls.PEER_REVIEW.value, cls.SYNTHESIS.value, cls.FAILED.value],
        }


class EvidenceConfidence(enum.Enum):
    """Verification status for evidence and claims."""
    VERIFIED = 'VERIFIED'
    PARTIALLY_VERIFIED = 'PARTIALLY_VERIFIED'
    UNVERIFIED = 'UNVERIFIED'
    CONTRADICTED = 'CONTRADICTED'


class HypothesisStatus(enum.Enum):
    """Status of a hypothesis in the evolutionary pipeline."""
    ACTIVE = 'ACTIVE'
    EVOLVED = 'EVOLVED'
    REJECTED = 'REJECTED'
    SURVIVED = 'SURVIVED'
    FALSIFIED = 'FALSIFIED'
    UNDER_REVIEW = 'UNDER_REVIEW'
    CHAMPION = 'CHAMPION'


class DebateVerdict(enum.Enum):
    """Possible verdicts from the Scientific Debate Arena."""
    SUPPORTED = 'SUPPORTED'
    PROMISING = 'PROMISING'
    UNCERTAIN = 'UNCERTAIN'
    WEAK = 'WEAK'
    REFUTED = 'REFUTED'
    INSUFFICIENT_EVIDENCE = 'INSUFFICIENT_EVIDENCE'


class ClaimType(enum.Enum):
    """Distinguish between different types of scientific assertions."""
    FACT = 'FACT'
    EVIDENCE = 'EVIDENCE'
    OBSERVATION = 'OBSERVATION'
    INFERENCE = 'INFERENCE'
    HYPOTHESIS = 'HYPOTHESIS'
    SIMULATION = 'SIMULATION'
    SPECULATION = 'SPECULATION'


@dataclass
class ResearchMission:
    """A complete autonomous research investigation."""
    mission_id: str
    objective: str
    domain: str
    mode: str = 'DEEP_RESEARCH'
    status: str = MissionStatus.PENDING.value
    user_constraints: str = ''
    research_depth: int = 5
    agent_budget: int = 100
    literature_budget: int = 50
    hypothesis_budget: int = 20
    simulation_budget: int = 50
    time_limit_hours: float = 2.0
    progress: float = 0.0
    current_phase: str = ''
    papers_found: int = 0
    claims_extracted: int = 0
    hypotheses_generated: int = 0
    hypotheses_survived: int = 0
    experiments_run: int = 0
    falsification_tests: int = 0
    peer_reviews: int = 0
    discovery_index: float = 0.0
    findings_json: str = '{}'
    evidence_json: str = '[]'
    checkpoint_json: str = '{}'
    error_message: str = ''
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentRun:
    """Record of a single agent execution within a mission."""
    mission_id: str
    research_id: str
    agent_role: str
    agent_class: str
    status: str = 'PENDING'
    input_summary: str = ''
    output_summary: str = ''
    output_data_json: str = '{}'
    confidence: float = 0.0
    execution_time_seconds: float = 0.0
    token_usage_json: str = '{}'
    error_message: str = ''
    attempt_number: int = 1
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MissionEvent:
    """A timestamped event in a mission's lifecycle for the activity log."""
    mission_id: str
    event_type: str
    message: str
    agent_role: str = ''
    phase: str = ''
    data_json: str = '{}'
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvolvingHypothesis:
    """A hypothesis within the evolutionary pipeline with full scoring dimensions."""
    hypothesis_id: str
    mission_id: str
    research_id: str
    statement: str
    domain: str
    generation: int = 0
    parent_ids_json: str = '[]'
    assumptions_json: str = '[]'
    supporting_evidence_json: str = '[]'
    contradicting_evidence_json: str = '[]'
    novelty_score: float = 0.0
    evidence_score: float = 0.0
    feasibility_score: float = 0.0
    impact_score: float = 0.0
    falsifiability_score: float = 0.0
    reproducibility_score: float = 0.0
    confidence: float = 0.0
    uncertainty: float = 1.0
    status: str = HypothesisStatus.ACTIVE.value
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    @property
    def parent_ids(self) -> List[str]:
        return json.loads(self.parent_ids_json) if self.parent_ids_json else []

    @property
    def assumptions(self) -> List[str]:
        return json.loads(self.assumptions_json) if self.assumptions_json else []

    @property
    def supporting_evidence(self) -> List[Dict[str, Any]]:
        return json.loads(self.supporting_evidence_json) if self.supporting_evidence_json else []

    @property
    def contradicting_evidence(self) -> List[Dict[str, Any]]:
        return json.loads(self.contradicting_evidence_json) if self.contradicting_evidence_json else []

    def composite_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted composite score across all dimensions."""
        w = weights or {
            'novelty': 0.20, 'evidence': 0.15, 'feasibility': 0.15,
            'impact': 0.15, 'falsifiability': 0.15, 'reproducibility': 0.10,
            'confidence': 0.10
        }
        return (
            w.get('novelty', 0.20) * self.novelty_score +
            w.get('evidence', 0.15) * self.evidence_score +
            w.get('feasibility', 0.15) * self.feasibility_score +
            w.get('impact', 0.15) * self.impact_score +
            w.get('falsifiability', 0.15) * self.falsifiability_score +
            w.get('reproducibility', 0.10) * self.reproducibility_score +
            w.get('confidence', 0.10) * self.confidence
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['composite_score'] = self.composite_score()
        return d


@dataclass
class DebateRecord:
    """Record of a scientific debate between advocate and skeptic agents."""
    debate_id: str
    mission_id: str
    hypothesis_id: str
    advocate_arguments_json: str = '[]'
    skeptic_arguments_json: str = '[]'
    evidence_used_json: str = '[]'
    evidence_quality: float = 0.0
    logical_weaknesses_json: str = '[]'
    unresolved_questions_json: str = '[]'
    methodology_review: str = ''
    statistical_review: str = ''
    verdict: str = DebateVerdict.UNCERTAIN.value
    judge_rationale: str = ''
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PeerReviewRecord:
    """Record of a structured peer review of the research process."""
    review_id: str
    mission_id: str
    research_id: str
    reviewer_role: str = 'PeerReviewer'
    methodology_assessment: str = ''
    evidence_assessment: str = ''
    reproducibility_assessment: str = ''
    statistical_validity: str = ''
    strengths_json: str = '[]'
    weaknesses_json: str = '[]'
    recommendations_json: str = '[]'
    overall_quality_score: float = 0.0
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FalsificationResult:
    """Result of a falsification attempt against a hypothesis."""
    falsification_id: str
    mission_id: str
    hypothesis_id: str
    criterion: str
    test_description: str
    test_type: str = 'conceptual'  # conceptual, empirical, simulation
    evidence_json: str = '{}'
    result: str = 'INCONCLUSIVE'  # PASSED, FAILED, INCONCLUSIVE
    explanation: str = ''
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FalsificationSummary:
    """Aggregate falsification results for a hypothesis."""
    hypothesis_id: str
    tests_attempted: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_inconclusive: int = 0

    @property
    def survival_score(self) -> float:
        """Percentage of tests the hypothesis survived. Not proof — just survival."""
        if self.tests_attempted == 0:
            return 0.0
        return (self.tests_passed / self.tests_attempted) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['survival_score'] = self.survival_score
        return d


@dataclass
class ContradictionRecord:
    """Record of contradictory evidence found for a claim."""
    contradiction_id: str
    mission_id: str
    claim_text: str
    claim_type: str = ClaimType.HYPOTHESIS.value
    supporting_evidence_json: str = '[]'
    contradicting_evidence_json: str = '[]'
    methodology_comparison: str = ''
    dataset_comparison: str = ''
    condition_comparison: str = ''
    contradiction_strength: float = 0.0
    possible_explanation: str = ''
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CounterfactualResult:
    """Result of a counterfactual analysis ('What if X changed?')."""
    counterfactual_id: str
    mission_id: str
    hypothesis_id: str
    question: str
    assumptions_json: str = '[]'
    model_description: str = ''
    evidence_json: str = '[]'
    predicted_outcome: str = ''
    uncertainty: float = 1.0
    limitations: str = ''
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeNode:
    """A typed node in the scientific knowledge graph."""
    node_id: str
    node_type: str  # Paper, Author, Claim, Hypothesis, Experiment, Dataset, Method, Concept, Result, ResearchGap, Institution, Citation
    label: str
    properties_json: str = '{}'
    mission_id: str = ''
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeEdge:
    """A typed edge in the scientific knowledge graph."""
    source_node_id: str
    target_node_id: str
    relation_type: str  # SUPPORTS, CONTRADICTS, CITES, USES_METHOD, TESTS, DERIVED_FROM, DEPENDS_ON, VALIDATES, REFUTES, RELATED_TO
    weight: float = 1.0
    properties_json: str = '{}'
    mission_id: str = ''
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiscoveryIndex:
    """Multi-dimensional scientific confidence score — the AION Discovery Index."""
    mission_id: str
    hypothesis_id: str
    evidence_quality: float = 0.0
    source_reliability: float = 0.0
    replication: float = 0.0
    agreement: float = 0.0
    contradiction_risk: float = 0.0
    methodological_robustness: float = 0.0
    falsifiability: float = 0.0
    reproducibility: float = 0.0
    novelty: float = 0.0
    uncertainty: float = 1.0

    @property
    def overall_score(self) -> float:
        """Calculate the transparent overall Discovery Index.

        Formula: Weighted mean of positive dimensions minus contradiction risk penalty.
        Weights are visible and configurable.
        """
        weights = {
            'evidence_quality': 0.15,
            'source_reliability': 0.10,
            'replication': 0.10,
            'agreement': 0.10,
            'methodological_robustness': 0.12,
            'falsifiability': 0.12,
            'reproducibility': 0.10,
            'novelty': 0.11,
        }
        raw = (
            weights['evidence_quality'] * self.evidence_quality +
            weights['source_reliability'] * self.source_reliability +
            weights['replication'] * self.replication +
            weights['agreement'] * self.agreement +
            weights['methodological_robustness'] * self.methodological_robustness +
            weights['falsifiability'] * self.falsifiability +
            weights['reproducibility'] * self.reproducibility +
            weights['novelty'] * self.novelty
        )
        # Apply contradiction risk as a penalty (0-100 scale)
        penalty = self.contradiction_risk * 0.10
        score = max(0.0, min(100.0, raw - penalty))
        return round(score, 1)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['overall_score'] = self.overall_score
        d['formula'] = (
            "Discovery Index = "
            "0.15*evidence_quality + 0.10*source_reliability + 0.10*replication + "
            "0.10*agreement + 0.12*methodological_robustness + 0.12*falsifiability + "
            "0.10*reproducibility + 0.11*novelty - 0.10*contradiction_risk"
        )
        return d


# ============================================================================
# AION X 2.0 — Comprehensive Provenance & Scientific OS Models
# ============================================================================

class ReplicationStatus(enum.Enum):
    NOT_ATTEMPTED = 'NOT_ATTEMPTED'
    PARTIAL = 'PARTIAL'
    SUCCESSFUL = 'SUCCESSFUL'
    FAILED = 'FAILED'
    INCONCLUSIVE = 'INCONCLUSIVE'
    NOT_REPRODUCIBLE = 'NOT_REPRODUCIBLE'


class ReplicationFailureReason(enum.Enum):
    NONE = 'NONE'
    PARAMETER_MISMATCH = 'PARAMETER_MISMATCH'
    DATASET_MISMATCH = 'DATASET_MISMATCH'
    MISSING_INFORMATION = 'MISSING_INFORMATION'
    IMPLEMENTATION_DIFFERENCE = 'IMPLEMENTATION_DIFFERENCE'
    STATISTICAL_DIFFERENCE = 'STATISTICAL_DIFFERENCE'
    RESOURCE_LIMIT = 'RESOURCE_LIMIT'
    NUMERICAL_INSTABILITY = 'NUMERICAL_INSTABILITY'
    POSSIBLE_REPLICATION_FAILURE = 'POSSIBLE_REPLICATION_FAILURE'
    INCONCLUSIVE = 'INCONCLUSIVE'


@dataclass
class Source:
    """A primary academic, dataset, or computational source."""
    source_id: str
    title: str
    source_type: str  # Journal, Conference, Preprint, Dataset, Repository, Simulation
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = ""
    url: Optional[str] = ""
    publisher: Optional[str] = ""
    is_peer_reviewed: bool = False
    retraction_status: str = "CLEAN"  # CLEAN, RETRACTED, CONCERN, UNKNOWN
    citation_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Passage:
    """An exact cited passage or excerpt from a source."""
    passage_id: str
    source_id: str
    section: str = ""
    page: Optional[int] = None
    text: str = ""
    confidence: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Dataset:
    """Dataset metadata and checksum for scientific reproducibility."""
    dataset_id: str
    name: str
    description: str = ""
    source_url: str = ""
    sha256_hash: str = ""
    num_samples: int = 0
    num_features: int = 0
    variables: List[str] = field(default_factory=list)
    license: str = "Open Access"
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Claim:
    """A single atomic scientific claim with epistemic classification and verification."""
    claim_id: str
    text: str
    claim_type: str = ClaimType.HYPOTHESIS.value  # FACT, EVIDENCE, OBSERVATION, INFERENCE, HYPOTHESIS, SIMULATION, SPECULATION
    verification_status: str = EvidenceConfidence.UNVERIFIED.value  # VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, CONTRADICTED
    source_ids: List[str] = field(default_factory=list)
    passage_ids: List[str] = field(default_factory=list)
    confidence: float = 0.5
    contradiction_ids: List[str] = field(default_factory=list)
    mission_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Evidence:
    """Structured empirical or theoretical evidence unit."""
    evidence_id: str
    claim_id: str
    source_id: str
    passage_id: str = ""
    evidence_type: str = "EMPIRICAL"  # EMPIRICAL, THEORETICAL, STATISTICAL, SIMULATION, BENCHMARK
    content: str = ""
    statistical_support: Dict[str, Any] = field(default_factory=dict)
    supports_claim: bool = True  # True if supports, False if contradicts
    confidence: float = 0.85
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StatisticalResult:
    """Rigorous statistical validation metrics."""
    stat_id: str
    experiment_id: str
    p_value: float = 0.05
    effect_size: float = 0.0
    r_squared: float = 0.0
    t_statistic: float = 0.0
    confidence_interval_low: float = 0.0
    confidence_interval_high: float = 0.0
    sample_size: int = 100
    test_type: str = "T-Test / Regression"
    assumptions_validated: bool = True
    assumptions_log: str = ""
    is_statistically_significant: bool = True
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Inference:
    """Logical derivation step from premises to conclusion."""
    inference_id: str
    premise_claim_ids: List[str]
    derived_claim_id: str
    reasoning_rule: str = "Deductive / Causal Transfer"
    strength: float = 0.8
    agent_id: str = "Innovator"
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Conclusion:
    """Final synthesised research conclusion with full provenance trace."""
    conclusion_id: str
    mission_id: str
    statement: str
    epistemic_class: str = "HYPOTHESIS"  # FACT, EVIDENCE, OBSERVATION, INFERENCE, HYPOTHESIS, SIMULATION, SPECULATION
    robustness: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    fragility_score: float = 0.3  # 0.0 (very robust) to 1.0 (extremely fragile)
    supporting_claim_ids: List[str] = field(default_factory=list)
    supporting_hypothesis_ids: List[str] = field(default_factory=list)
    confidence: float = 0.8
    contradiction_risk: float = 0.2
    recommended_next_action: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProvenanceEdge:
    """Explicit relationship in the evidence lineage graph."""
    source_entity_id: str
    source_entity_type: str
    target_entity_id: str
    target_entity_type: str
    relation: str  # SOURCE_CONTAINS_PASSAGE, PASSAGE_SUPPORTS_CLAIM, CLAIM_SUPPORTS_HYPOTHESIS, etc.
    mission_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DeathCertificate:
    """Formal post-mortem analysis for refuted or falsified hypotheses."""
    certificate_id: str
    hypothesis_id: str
    final_statement: str
    cause_of_failure: str
    fatal_evidence: str
    experiment_responsible: str
    failed_prediction: str
    confidence: float
    replication_status: str
    assumptions_violated: List[str] = field(default_factory=list)
    surviving_components: List[str] = field(default_factory=list)
    reusable_lessons: List[str] = field(default_factory=list)
    falsification_stage: str = "Adversarial Simulation"
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FailedExperiment:
    """Permanent record of a failed experimental trial."""
    failure_id: str
    hypothesis_id: str
    experiment_id: str
    failure_type: str  # PARAMETER_COLLAPSE, CONVERGENCE_FAILURE, RESOURCE_LIMIT, CODE_EXCEPTION, ASSUMPTION_VIOLATION
    parameters: Dict[str, Any] = field(default_factory=dict)
    environment: str = "Sandbox AST v2.0"
    observations: str = ""
    diagnosis: str = ""
    confidence: float = 0.9
    learned_constraint: str = ""
    future_recommendation: str = ""
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReplicationAttempt:
    """Computational replication evaluation record."""
    replication_id: str
    paper_id: str
    experiment_id: str
    reported_result: str
    reproduced_result: str
    absolute_difference: float = 0.0
    relative_difference: float = 0.0
    uncertainty: float = 0.05
    parameter_match: float = 1.0
    dataset_match: float = 1.0
    method_match: float = 1.0
    execution_status: str = "SUCCESSFUL"
    replication_status: str = ReplicationStatus.SUCCESSFUL.value
    failure_reason: str = ReplicationFailureReason.NONE.value
    multi_run_scores: List[float] = field(default_factory=list)
    reproducibility_score: float = 92.0
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CounterfactualExperiment:
    """Result of systematic counterfactual perturbation testing."""
    counterfactual_id: str
    hypothesis_id: str
    varied_dimension: str  # ASSUMPTION, PARAMETER, CAUSAL_RELATION, NOISE, BOUNDARY, SAMPLE_SIZE
    baseline_value: str
    perturbed_value: str
    robustness_score: float = 85.0
    is_fragile: bool = False
    failure_point_identified: str = ""
    observations: str = ""
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchTreeNode:
    """A node in the persistent hierarchical research tree."""
    node_id: str
    parent_id: Optional[str]
    node_type: str  # QUESTION, HYPOTHESIS, VARIANT, EXPERIMENT, EVIDENCE, CONTRADICTION, OUTCOME
    title: str
    status: str = "ACTIVE"
    confidence: float = 0.8
    mission_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    children_ids: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TournamentArgument:
    """Individual round argument in the Adversarial Research Tournament."""
    argument_id: str
    tournament_id: str
    round_number: int
    round_name: str  # Logical, Evidence, Causal, Statistical, Confounder, Counterexample, Replication, Experimental
    speaker_role: str  # Advocate, Skeptic, Null-Hypothesis, Methodologist, Statistician, Falsifier
    claim_text: str
    attack_text: str
    defense_text: str
    attack_strength: float = 0.0
    defense_strength: float = 0.0
    unresolved_objection: str = ""
    evidence_refs: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KillChainReport:
    """Comprehensive 10-stage hypothesis stress-test attack report."""
    hypothesis_id: str
    initial_score: float = 75.0
    literature_attack_score: float = 70.0
    contradiction_score: float = 65.0
    assumption_score: float = 68.0
    simulation_score: float = 80.0
    replication_score: float = 78.0
    statistical_score: float = 82.0
    final_survival_score: float = 73.0  # Empirical resilience score
    strongest_support: str = ""
    strongest_contradiction: str = ""
    critical_assumptions: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    recommended_next_action: str = ""
    disclaimer: str = "Empirical resilience score represents survival against simulated falsification; it does not constitute mathematical or physical proof."
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RedTeamReport:
    """Full system-wide adversarial audit of a scientific discovery."""
    mission_id: str
    literature_integrity: float = 88.0
    evidence_integrity: float = 85.0
    causal_validity: float = 78.0
    statistical_validity: float = 84.0
    reproducibility_rating: float = 80.0
    novelty_rating: float = 86.0
    overall_research_risk: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    findings: List[str] = field(default_factory=list)
    cascade_warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActiveResearchRecommendation:
    """Ranked next-best-research action based on Information Gain / Cost."""
    action_id: str
    mission_id: str
    action_type: str  # REPLICATION_EXPERIMENT, PARAMETER_SWEEP, CONTRADICTION_SEARCH, CAUSAL_VERIFICATION
    target_hypothesis_id: str
    title: str
    expected_information_gain: float = 0.75  # 0.0 to 1.0
    estimated_cost_usd: Optional[float] = None
    estimated_duration_hours: Optional[float] = None
    risk_level: str = "Low"
    feasibility_score: float = 85.0
    hypothesis_discrimination_power: float = 0.88
    recommended_rank: int = 1
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkRun:
    """Benchmark execution tracking and empirical metrics."""
    run_id: str
    task_name: str
    mode: str = "BENCHMARK"
    discovery_rate: float = 90.0
    evidence_accuracy: float = 95.0
    citation_accuracy: float = 98.0
    contradiction_recall: float = 90.0
    latency_seconds: float = 1.5
    compute_cost_usd: float = 0.005
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



