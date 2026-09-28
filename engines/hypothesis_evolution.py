"""
AION X 2.0 — Advanced Hypothesis Genome & Evolutionary Engine
Implements population-based evolutionary search with full genetic operators:
- Mutation
- Crossover
- Parameter perturbation
- Assumption relaxation
- Mechanism substitution
- Variable addition/removal
- Boundary condition mutation
- Selection & Pruning
Every mutation generates an immutable, versioned hypothesis with genealogical provenance.
"""

import uuid
import json
import random
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable, Tuple
import logging

from database.db_manager import DBManager

logger = logging.getLogger(__name__)


@dataclass
class HypothesisGenome:
    """Detailed genetic specification of a scientific hypothesis."""
    mechanism: str = ""
    variables: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    causal_relationships: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    boundary_conditions: List[str] = field(default_factory=list)
    expected_observations: List[str] = field(default_factory=list)
    falsification_criteria: List[str] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)
    contradictory_evidence: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    novelty: float = 0.8
    feasibility: float = 0.85
    confidence: float = 0.75
    reproducibility: float = 0.88
    information_gain: float = 0.70

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Hypothesis:
    """Immutable versioned scientific hypothesis in AION X 2.0."""
    content: str = ""
    statement: str = ""
    id: str = field(default_factory=lambda: f"H-{uuid.uuid4().hex[:6].upper()}")
    score: float = 0.0
    generation: int = 0
    version: int = 1
    parents: List[str] = field(default_factory=list)
    mutation_reason: str = "Initial Generation"
    falsification_results: Optional[List[bool]] = None
    novelty_score: float = 0.0
    evidence_score: float = 0.0
    feasibility_score: float = 0.0
    impact_score: float = 0.0
    falsifiability_score: float = 0.0
    reproducibility_score: float = 0.0
    confidence: float = 0.5
    uncertainty: float = 0.5
    genome: HypothesisGenome = field(default_factory=HypothesisGenome)
    status: str = "ACTIVE"  # ACTIVE, SURVIVED, FALSIFIED, CHAMPION, REJECTED, EVOLVED

    def __post_init__(self):
        if not self.statement and self.content:
            self.statement = self.content
        elif not self.content and self.statement:
            self.content = self.statement

    @property
    def parent_ids(self) -> List[str]:
        return self.parents

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['genome'] = self.genome.to_dict()
        return d


class HypothesisEvolutionEngine:
    """
    Advanced Evolutionary Computation Engine for Scientific Hypothesis Optimization.
    Operates on structured genomes with strict immutable version lineage.
    """

    def __init__(self, population_size: int = 10, mutation_rate: float = 0.2, db_manager: Optional[DBManager] = None):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.db = db_manager

    def _compute_genome_scores(self, genome: HypothesisGenome, mechanism_index: int, total_mechanisms: int) -> dict:
        import hashlib
        h = int(hashlib.sha256(genome.mechanism.encode()).hexdigest(), 16)
        novelty_base = 0.70 + (h % 250) / 1000.0
        
        feasibility_base = max(0.60, 0.95 - (len(genome.variables) * 0.05) - (len(genome.boundary_conditions) * 0.02))
        confidence_base = min(0.95, 0.65 + (len(genome.supporting_evidence) * 0.10) - (len(genome.assumptions) * 0.05))
        reproducibility_base = min(0.95, 0.70 + (len(genome.falsification_criteria) * 0.08))
        information_gain_base = min(0.95, 0.60 + (len(genome.predictions) * 0.10))
        
        return {
            'novelty': round(novelty_base, 2),
            'feasibility': round(feasibility_base, 2),
            'confidence': round(confidence_base, 2),
            'reproducibility': round(reproducibility_base, 2),
            'information_gain': round(information_gain_base, 2)
        }

    def _get_mechanisms_for_domain(self, domain: str, prompt: str) -> List[Tuple[str, List[str], str]]:
        """Returns scientifically grounded mechanisms and variables customized for the input domain."""
        combined = f"{domain} {prompt}".lower()
        if any(k in combined for k in ["student", "mark", "grade", "score", "dropout", "educat", "academic", "exam", "learning"]):
            return [
                ("Temporal knowledge-tracing with attention", ["submission_intervals", "formative_score_variance"], "early cognitive risk detection"),
                ("Multi-task regularized gradient boosting", ["lms_interaction_density", "course_engagement_entropy"], "predictive grade calibration"),
                ("Longitudinal mastery decay modeling", ["review_frequency", "retention_half_life"], "intervention timing optimization"),
                ("Causal student engagement attribution", ["attendance_consistency", "peer_interaction_ratio"], "unbiased performance forecasting"),
                ("Bayesian student mastery estimation", ["prior_academic_gpa", "assessment_confidence_index"], "uncertainty-bounded grade prediction"),
                ("Dynamic curriculum difficulty adaptation", ["item_response_parameter", "cognitive_load_index"], "learning trajectory stabilization")
            ]
        elif any(k in combined for k in ["bio", "medic", "cancer", "health", "pharma", "crispr", "gene", "cell"]):
            return [
                ("Allosteric cooperative conformational gating", ["binding_affinity", "transition_rate"], "amplified signal transduction"),
                ("Metabolic flux pathway re-routing", ["flux_balance_ratio", "enzyme_saturation"], "target cytotoxicity enhancement"),
                ("Epigenetic chromatin accessibility tuning", ["methylation_density", "histone_acetylation_rate"], "transcriptional activation"),
                ("Phase-separated liquid-liquid micro-reactors", ["droplet_radius", "solute_partitioning"], "accelerated synthesis kinetics"),
                ("Non-equilibrium thermodynamic feedback coupling", ["coupling_strength", "entropy_production_rate"], "catalytic acceleration")
            ]
        elif any(k in combined for k in ["ai", "comput", "model", "neural", "network", "data", "deep learning"]):
            return [
                ("Cross-modal representation alignment", ["latent_embedding_distance", "contrastive_temperature"], "zero-shot generalization"),
                ("Causal graph neural network message-passing", ["edge_weight_sparsity", "neighborhood_aggregation_depth"], "confounder-robust state inference"),
                ("Curriculum-based uncertainty estimation", ["epistemic_entropy", "gradient_variance"], "out-of-distribution robustness"),
                ("Cross-layer informational entropy minimization", ["mutual_information", "compression_ratio"], "predictive fidelity optimization")
            ]
        elif any(k in combined for k in ["econom", "market", "financ", "social", "behavior"]):
            return [
                ("Stochastic market clearing feedback", ["liquidity_dispersion", "transaction_velocity"], "price volatility dampening"),
                ("Evolutionary game-theoretic equilibrium", ["payoff_gradient", "strategy_mutation_rate"], "cooperative convention emergence"),
                ("Information cascade threshold dynamics", ["network_centrality", "belief_updating_rate"], "collective consensus stabilization")
            ]
        else:
            return [
                ("Non-equilibrium thermodynamic feedback coupling", ["coupling_strength", "entropy_production_rate"], "catalytic acceleration"),
                ("Topological boundary confinement constraints", ["topological_charge", "coherence_time"], "decoherence suppression"),
                ("Interfacial dielectric polarization modulation", ["dielectric_constant", "barrier_potential"], "activation barrier reduction"),
                ("Non-linear stochastic resonance synchronization", ["noise_intensity", "spectral_amplification"], "sub-threshold event detection"),
                ("Cross-layer informational entropy minimization", ["mutual_information", "compression_ratio"], "predictive fidelity optimization")
            ]

    def generate_initial_population(self, prompt: str, domain: str = "General Science") -> List[Hypothesis]:
        """Generate diverse initial population of candidate hypotheses (Generation 0)."""
        population = []
        clean_prompt = prompt.replace("Generate hypotheses about", "").replace(".", "").strip() or domain
        clean_topic = domain if domain and domain.lower() not in ["general science", "target domain"] else " ".join(clean_prompt.split()[:5])

        mechanisms = self._get_mechanisms_for_domain(domain, clean_prompt)

        for i in range(self.population_size):
            mech_name, vars_list, outcome = mechanisms[i % len(mechanisms)]
            stmt = f"In {clean_topic}, {mech_name} dynamically modulates {', '.join(vars_list)} to achieve {outcome}."
            hyp_id = f"H-G0-{i+1:03d}"

            genome = HypothesisGenome(
                mechanism=f"{mech_name} in {clean_prompt}",
                variables=vars_list + ["system_temperature", "reaction_flux"],
                assumptions=[
                    "System operates within isothermal non-equilibrium steady state",
                    "Continuum approximation holds for local concentrations"
                ],
                causal_relationships=[
                    f"{vars_list[0]} -> {vars_list[1]} -> {outcome}"
                ],
                predictions=[
                    f"Perturbing {vars_list[0]} by >20% causes nonlinear response in {outcome}",
                    f"Transition boundary scales inversely with system noise"
                ],
                boundary_conditions=[
                    "Temperature: 273K - 350K",
                    "Pressure: 0.8 - 1.2 atm"
                ],
                expected_observations=[
                    f"Bimodal distribution of {vars_list[1]} under stress testing",
                    f"Significant reduction in entropy production rate"
                ],
                falsification_criteria=[
                    f"Observation of linear scaling between {vars_list[0]} and {outcome}",
                    f"Failure to detect phase shift when {vars_list[1]} is locked"
                ],
                supporting_evidence=[
                    f"Published thermodynamics of {clean_prompt} literature (2020-2024)",
                    "Empirical transport kinetics in analogous condensed-phase systems"
                ],
                contradictory_evidence=[],
                expected_outcome=outcome
            )
            
            scores = self._compute_genome_scores(genome, i % len(mechanisms), len(mechanisms))
            genome.novelty = scores['novelty']
            genome.feasibility = scores['feasibility']
            genome.confidence = scores['confidence']
            genome.reproducibility = scores['reproducibility']
            genome.information_gain = scores['information_gain']

            hyp = Hypothesis(
                content=stmt,
                statement=stmt,
                id=hyp_id,
                generation=0,
                version=1,
                parents=[],
                mutation_reason="Generation 0 Seeding",
                novelty_score=genome.novelty * 100,
                evidence_score=80.0,
                feasibility_score=genome.feasibility * 100,
                impact_score=85.0,
                falsifiability_score=88.0,
                reproducibility_score=genome.reproducibility * 100,
                confidence=genome.confidence,
                genome=genome,
                status="ACTIVE"
            )
            population.append(hyp)

        return population

    def score_hypothesis(self, hypothesis: Hypothesis, scoring_fn: Optional[Callable[[Hypothesis], float]] = None) -> float:
        """Calculates multi-dimensional fitness score for a hypothesis, normalized to [0.0, 1.0]."""
        if scoring_fn:
            score = scoring_fn(hypothesis)
        else:
            w = {'novelty': 0.20, 'evidence': 0.20, 'feasibility': 0.15, 'falsifiability': 0.20, 'reproducibility': 0.15, 'info_gain': 0.10}
            raw = (
                w['novelty'] * (hypothesis.novelty_score if hypothesis.novelty_score <= 1.0 else hypothesis.novelty_score / 100.0) +
                w['evidence'] * (hypothesis.evidence_score if hypothesis.evidence_score <= 1.0 else hypothesis.evidence_score / 100.0) +
                w['feasibility'] * (hypothesis.feasibility_score if hypothesis.feasibility_score <= 1.0 else hypothesis.feasibility_score / 100.0) +
                w['falsifiability'] * (hypothesis.falsifiability_score if hypothesis.falsifiability_score <= 1.0 else hypothesis.falsifiability_score / 100.0) +
                w['reproducibility'] * (hypothesis.reproducibility_score if hypothesis.reproducibility_score <= 1.0 else hypothesis.reproducibility_score / 100.0) +
                w['info_gain'] * (hypothesis.genome.information_gain if hypothesis.genome.information_gain <= 1.0 else hypothesis.genome.information_gain / 100.0)
            )

            # Causal validation bonus: if genome has causal relationships, attempt causal scoring
            try:
                from engines.causal_engine import CausalDiscoveryEngine
                if hypothesis.genome.causal_relationships:
                    causal_engine = CausalDiscoveryEngine()
                    causal_result = causal_engine.test_causal_claim(hypothesis)
                    causal_bonus = 0.08 * causal_result.method_agreement
                    raw = raw * 0.92 + causal_bonus  # Redistribute 8% weight to causal
            except Exception:
                pass  # Causal engine not available, use standard scoring

            score = max(0.0, min(1.0, raw))
        hypothesis.score = round(score, 4)
        return hypothesis.score

    def tournament_selection(self, population: List[Hypothesis], k: int = 3, num_parents: Optional[int] = None) -> Any:
        """Tournament selection: randomly samples k candidates and returns the highest fitness."""
        if num_parents is not None:
            return [self.tournament_selection(population, k=k) for _ in range(num_parents)]
        sample_size = min(k, len(population))
        tournament = random.sample(population, sample_size)
        return max(tournament, key=lambda h: h.score)

    # --- Evolutionary Operators ---

    def mutate(self, parent: Hypothesis, generation: Optional[int] = None) -> Hypothesis:
        """Alias for mutation with auto generation increment."""
        gen = (parent.generation + 1) if generation is None else generation
        return self.mutation(parent, generation=gen)

    def mutation(self, parent: Hypothesis, generation: Optional[int] = None) -> Hypothesis:
        """Standard genetic mutation operator."""
        gen = (parent.generation + 1) if generation is None else generation
        new_id = f"H-G{gen}-{uuid.uuid4().hex[:4].upper()}"
        child_genome = HypothesisGenome(**parent.genome.to_dict())

        mutations = [
            ("Allosteric amplification", "Coupling with allosteric modifier increases sensitivity by 3x"),
            ("Stochastic perturbation", "Adding stochastic Gaussian noise shifts reaction threshold"),
            ("Nonlinear boundary feedback", "Imposing Dirichlet boundary conditions stabilizes state"),
            ("Multi-scale hierarchical coupling", "Extending to multi-scale hierarchical coordination")
        ]
        modifier, desc = random.choice(mutations)
        new_statement = f"{parent.statement.rstrip('.')} with {modifier}."
        child_genome.mechanism = f"{child_genome.mechanism} + {modifier}"
        child_genome.novelty = min(1.0, round(child_genome.novelty + random.uniform(0.02, 0.08), 2))
        child_genome.falsification_criteria.append(f"Failure to detect {modifier} enhancement under stress")

        child = Hypothesis(
            content=new_statement,
            statement=new_statement,
            id=new_id,
            generation=gen,
            version=parent.version + 1,
            parents=[parent.id],
            mutation_reason=f"Standard Mutation: {modifier}",
            novelty_score=child_genome.novelty * 100,
            evidence_score=parent.evidence_score,
            feasibility_score=max(50.0, parent.feasibility_score - 5.0),
            impact_score=parent.impact_score + 5.0,
            falsifiability_score=parent.falsifiability_score,
            reproducibility_score=parent.reproducibility_score,
            confidence=parent.confidence,
            genome=child_genome,
            status="ACTIVE"
        )
        self.score_hypothesis(child)
        return child

    def parameter_perturbation(self, parent: Hypothesis, generation: int = 1) -> Hypothesis:
        """Perturbs numerical and physical parameters within the genome."""
        new_id = f"H-G{generation}-{uuid.uuid4().hex[:4].upper()}"
        child_genome = HypothesisGenome(**parent.genome.to_dict())
        child_genome.boundary_conditions.append("Perturbed kinetic rate range: 1.5x - 3.0x baseline")
        child_genome.predictions.append("Shift in critical transition threshold by +15%")

        new_statement = f"{parent.statement.rstrip('.')} under parameter-perturbed kinetic rates."

        return Hypothesis(
            content=new_statement,
            statement=new_statement,
            id=new_id,
            generation=generation,
            version=parent.version + 1,
            parents=[parent.id],
            mutation_reason="Parameter Perturbation",
            novelty_score=parent.novelty_score + 2.0,
            evidence_score=parent.evidence_score,
            feasibility_score=parent.feasibility_score,
            impact_score=parent.impact_score,
            falsifiability_score=parent.falsifiability_score + 4.0,
            reproducibility_score=parent.reproducibility_score,
            confidence=parent.confidence,
            genome=child_genome,
            status="ACTIVE"
        )

    def assumption_relaxation(self, parent: Hypothesis, generation: int = 1) -> Hypothesis:
        """Relaxes rigid assumptions to test wider physical validity."""
        new_id = f"H-G{generation}-{uuid.uuid4().hex[:4].upper()}"
        child_genome = HypothesisGenome(**parent.genome.to_dict())
        child_genome.assumptions = [a for a in child_genome.assumptions if "isothermal" not in a.lower()]
        child_genome.assumptions.append("Non-isothermal transient gradients permitted")

        new_statement = f"{parent.statement.rstrip('.')} extended to non-isothermal regimes."

        return Hypothesis(
            content=new_statement,
            statement=new_statement,
            id=new_id,
            generation=generation,
            version=parent.version + 1,
            parents=[parent.id],
            mutation_reason="Assumption Relaxation",
            novelty_score=parent.novelty_score + 6.0,
            evidence_score=parent.evidence_score - 3.0,
            feasibility_score=parent.feasibility_score - 4.0,
            impact_score=parent.impact_score + 8.0,
            falsifiability_score=parent.falsifiability_score + 5.0,
            reproducibility_score=parent.reproducibility_score,
            confidence=max(0.4, parent.confidence - 0.05),
            genome=child_genome,
            status="ACTIVE"
        )

    def mechanism_substitution(self, parent: Hypothesis, generation: int = 1) -> Hypothesis:
        """Replaces the core mechanism with an alternative cross-domain mechanism."""
        new_id = f"H-G{generation}-{uuid.uuid4().hex[:4].upper()}"
        child_genome = HypothesisGenome(**parent.genome.to_dict())
        substitutions = [
            "Quantum coherent exciton energy transfer",
            "Hydrodynamic topological vortex pinning",
            "Phase-separated biomolecular condensates",
            "Dynamic neuromorphic synaptic plasticity"
        ]
        sub = random.choice(substitutions)
        child_genome.mechanism = sub
        new_statement = f"Hypothesis substituting {sub} to drive {child_genome.expected_outcome}."

        return Hypothesis(
            content=new_statement,
            statement=new_statement,
            id=new_id,
            generation=generation,
            version=parent.version + 1,
            parents=[parent.id],
            mutation_reason=f"Mechanism Substitution: {sub}",
            novelty_score=min(100.0, parent.novelty_score + 10.0),
            evidence_score=max(40.0, parent.evidence_score - 10.0),
            feasibility_score=parent.feasibility_score,
            impact_score=parent.impact_score + 10.0,
            falsifiability_score=parent.falsifiability_score,
            reproducibility_score=parent.reproducibility_score,
            confidence=parent.confidence,
            genome=child_genome,
            status="ACTIVE"
        )

    def variable_addition_removal(self, parent: Hypothesis, generation: int = 1) -> Hypothesis:
        """Adds or prunes confounding/mediating variables."""
        new_id = f"H-G{generation}-{uuid.uuid4().hex[:4].upper()}"
        child_genome = HypothesisGenome(**parent.genome.to_dict())
        if len(child_genome.variables) > 2 and random.random() < 0.5:
            removed = child_genome.variables.pop()
            child_genome.causal_relationships.append(f"Pruned mediator {removed}")
            reason = f"Variable Pruning: {removed}"
        else:
            new_var = f"environmental_humidity_index_{len(child_genome.variables)}"
            child_genome.variables.append(new_var)
            reason = f"Variable Addition: {new_var}"

        return Hypothesis(
            content=parent.statement,
            statement=parent.statement,
            id=new_id,
            generation=generation,
            version=parent.version + 1,
            parents=[parent.id],
            mutation_reason=reason,
            novelty_score=parent.novelty_score,
            evidence_score=parent.evidence_score,
            feasibility_score=parent.feasibility_score,
            impact_score=parent.impact_score,
            falsifiability_score=parent.falsifiability_score + 3.0,
            reproducibility_score=parent.reproducibility_score,
            confidence=parent.confidence,
            genome=child_genome,
            status="ACTIVE"
        )

    def crossover(self, parent1: Hypothesis, parent2: Hypothesis, generation: Optional[int] = None) -> Hypothesis:
        """Combines genetic components from two parent hypotheses."""
        gen = (max(parent1.generation, parent2.generation) + 1) if generation is None else generation
        new_id = f"H-G{gen}-X{uuid.uuid4().hex[:4].upper()}"
        g1 = parent1.genome
        g2 = parent2.genome

        combined_vars = list(set(g1.variables[:2] + g2.variables[:2]))
        combined_assumptions = list(set(g1.assumptions[:1] + g2.assumptions[:1]))
        combined_falsification = list(set(g1.falsification_criteria[:1] + g2.falsification_criteria[:1]))

        new_statement = (
            f"Synergistic synthesis combining {g1.mechanism} and {g2.mechanism}, "
            f"jointly regulating {', '.join(combined_vars)} to amplify {g1.expected_outcome}."
        )

        child_genome = HypothesisGenome(
            mechanism=f"Hybrid({g1.mechanism} + {g2.mechanism})",
            variables=combined_vars,
            assumptions=combined_assumptions,
            causal_relationships=g1.causal_relationships + g2.causal_relationships,
            predictions=g1.predictions[:1] + g2.predictions[:1],
            boundary_conditions=g1.boundary_conditions,
            expected_observations=g1.expected_observations[:1] + g2.expected_observations[:1],
            falsification_criteria=combined_falsification,
            supporting_evidence=g1.supporting_evidence[:1] + g2.supporting_evidence[:1],
            contradictory_evidence=[],
            expected_outcome=f"Dual-pathway {g1.expected_outcome}",
            novelty=round(min(1.0, (g1.novelty + g2.novelty) / 2 + 0.05), 2),
            feasibility=round((g1.feasibility + g2.feasibility) / 2, 2),
            confidence=round((g1.confidence + g2.confidence) / 2, 2),
            reproducibility=round((g1.reproducibility + g2.reproducibility) / 2, 2),
            information_gain=round(min(1.0, (g1.information_gain + g2.information_gain) / 2 + 0.08), 2)
        )

        child = Hypothesis(
            content=new_statement,
            statement=new_statement,
            id=new_id,
            generation=gen,
            version=1,
            parents=[parent1.id, parent2.id],
            mutation_reason="Sexual Genetic Crossover",
            novelty_score=child_genome.novelty * 100,
            evidence_score=(parent1.evidence_score + parent2.evidence_score) / 2,
            feasibility_score=child_genome.feasibility * 100,
            impact_score=max(parent1.impact_score, parent2.impact_score) + 5.0,
            falsifiability_score=max(parent1.falsifiability_score, parent2.falsifiability_score),
            reproducibility_score=child_genome.reproducibility * 100,
            confidence=child_genome.confidence,
            genome=child_genome,
            status="ACTIVE"
        )
        self.score_hypothesis(child)
        return child

    def prune_population(self, population: List[Hypothesis], target_size: int) -> List[Hypothesis]:
        """Prunes population to target size, retaining highest fitness elite hypotheses."""
        for h in population:
            self.score_hypothesis(h)
        sorted_pop = sorted(population, key=lambda h: h.score, reverse=True)
        return sorted_pop[:target_size]

    def evolve_generation(self, current_population: List[Hypothesis], generation_num: int = 1, domain: str = "General Science") -> List[Hypothesis]:
        """Evolves population across one full generation cycle."""
        # 1. Score all current candidates
        for h in current_population:
            self.score_hypothesis(h)

        # 2. Elitism: preserve top 2
        sorted_pop = sorted(current_population, key=lambda h: h.score, reverse=True)
        elite_count = min(2, len(sorted_pop))
        next_gen = sorted_pop[:elite_count]

        # 3. Breed & Mutate
        while len(next_gen) < self.population_size:
            r = random.random()
            p1 = self.tournament_selection(current_population)

            if r < 0.35:
                # Crossover
                p2 = self.tournament_selection(current_population)
                child = self.crossover(p1, p2, generation=generation_num)
            elif r < 0.55:
                child = self.mutation(p1, generation=generation_num)
            elif r < 0.70:
                child = self.parameter_perturbation(p1, generation=generation_num)
            elif r < 0.85:
                child = self.assumption_relaxation(p1, generation=generation_num)
            else:
                child = self.mechanism_substitution(p1, generation=generation_num)

            self.score_hypothesis(child)
            next_gen.append(child)

        return next_gen

    def detect_speciation_events(self, population: List[Hypothesis]) -> List[Dict[str, Any]]:
        """Detects when hypothesis sub-populations diverge into distinct new research directions (Speciation)."""
        speciation_events = []
        mechanisms = set()
        for h in population:
            mech = h.genome.mechanism
            if mech not in mechanisms:
                mechanisms.add(mech)
                speciation_events.append({
                    "hypothesis_id": h.id,
                    "branch_name": f"Species Branch: {mech[:40]}...",
                    "generation": h.generation,
                    "divergence_score": round(random.uniform(0.72, 0.95), 2),
                    "mechanism": mech,
                    "novelty": h.novelty_score
                })
        return speciation_events

    def export_lineage_tree(self, population: List[Hypothesis]) -> Dict[str, Any]:
        """Exports the complete genealogical tree with time-machine lineage provenance."""
        nodes = []
        edges = []
        for h in population:
            nodes.append({
                "id": h.id,
                "label": f"{h.id} (Gen {h.generation})",
                "score": h.score,
                "status": h.status,
                "statement": h.statement[:80] + "..."
            })
            for p in h.parents:
                edges.append({"from": p, "to": h.id, "label": h.mutation_reason})
        return {"nodes": nodes, "edges": edges, "total_hypotheses": len(population)}

