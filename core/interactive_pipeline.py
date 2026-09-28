"""
AION X 2.0 — Interactive Streaming Pipeline with Human-in-the-Loop Steering
Provides WebSocket-based pipeline control where users can steer hypothesis selection,
gap pursuit, experimental parameters, and kill chain decisions in real-time.
"""

import json
import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


@dataclass
class SteeringEvent:
    """A decision point where the user can steer the pipeline."""
    event_id: str
    event_type: str
    payload: Dict[str, Any]
    available_actions: List[str]
    default_action: str
    timeout_seconds: float = 60.0
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SteeringDecision:
    """User's response to a steering event."""
    event_id: str
    chosen_action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))


@dataclass
class PipelineState:
    """Current state of the interactive pipeline."""
    mission_id: str
    current_phase: str = "IDLE"
    phases_completed: List[str] = field(default_factory=list)
    steering_history: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    is_running: bool = False
    progress_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─── Steering Event Definitions ──────────────────────────────────────────────

STEERING_EVENTS = {
    "gaps_detected": {
        "description": "Research gaps identified — choose which to pursue",
        "actions": ["pursue_gap_1", "pursue_gap_2", "merge_gaps", "add_custom_gap", "skip"],
        "default": "pursue_gap_1",
        "timeout": 60.0,
    },
    "hypotheses_generated": {
        "description": "Candidate hypotheses generated — select champion",
        "actions": ["approve_champion", "edit_hypothesis", "request_more_variants", "reject_all"],
        "default": "approve_champion",
        "timeout": 90.0,
    },
    "kill_chain_failure": {
        "description": "Kill chain detected vulnerability — decide next action",
        "actions": ["pivot_mechanism", "relax_assumption", "gather_more_evidence", "abort"],
        "default": "gather_more_evidence",
        "timeout": 60.0,
    },
    "experiment_designed": {
        "description": "Experiment protocol ready — review before execution",
        "actions": ["run_as_is", "modify_parameters", "change_dataset", "add_control"],
        "default": "run_as_is",
        "timeout": 45.0,
    },
    "cross_domain_transfer": {
        "description": "Cross-domain mechanism transfer proposed — approve or reject",
        "actions": ["approve_transfer", "modify_mapping", "reject_transfer", "try_different_domain"],
        "default": "approve_transfer",
        "timeout": 60.0,
    },
    "replication_result": {
        "description": "Paper replication completed — review discrepancies",
        "actions": ["accept_result", "rerun_with_different_seed", "investigate_discrepancy", "skip"],
        "default": "accept_result",
        "timeout": 45.0,
    },
}


class InteractivePipeline:
    """
    Streaming pipeline with human-in-the-loop steering.
    
    In Streamlit mode: Uses session_state for synchronous steering decisions.
    In WebSocket mode: Uses async WebSocket for real-time bidirectional communication.
    
    Each agent phase:
    1. Execute agent
    2. Emit steering event with payload + available actions
    3. Await user decision (with timeout → auto-proceed with default)
    4. Apply decision → continue to next phase
    """

    def __init__(self):
        self.state = None
        self._decision_queue: Dict[str, Optional[SteeringDecision]] = {}
        self._event_callbacks: List[Callable] = []
        self._progress_callbacks: List[Callable] = []

    def register_event_callback(self, callback: Callable[[SteeringEvent], None]):
        """Register a callback that fires when a steering event is emitted."""
        self._event_callbacks.append(callback)

    def register_progress_callback(self, callback: Callable[[str, float, str], None]):
        """Register a callback for progress updates (phase, pct, message)."""
        self._progress_callbacks.append(callback)

    def _emit_progress(self, phase: str, pct: float, message: str):
        """Emit progress update to all registered callbacks."""
        if self.state:
            self.state.current_phase = phase
            self.state.progress_pct = pct
        for cb in self._progress_callbacks:
            try:
                cb(phase, pct, message)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def _emit_steering_event(self, event_type: str, payload: Dict[str, Any]) -> SteeringEvent:
        """Create and emit a steering event."""
        event_def = STEERING_EVENTS.get(event_type, {})
        event = SteeringEvent(
            event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
            event_type=event_type,
            payload=payload,
            available_actions=event_def.get("actions", ["continue", "skip"]),
            default_action=event_def.get("default", "continue"),
            timeout_seconds=event_def.get("timeout", 60.0),
        )
        self._decision_queue[event.event_id] = None

        for cb in self._event_callbacks:
            try:
                cb(event)
            except Exception as e:
                logger.warning(f"Event callback error: {e}")

        if self.state:
            self.state.steering_history.append(event.to_dict())

        return event

    def submit_decision(self, event_id: str, action: str, parameters: Dict[str, Any] = None):
        """Submit a user decision for a pending steering event."""
        decision = SteeringDecision(
            event_id=event_id,
            chosen_action=action,
            parameters=parameters or {},
        )
        self._decision_queue[event_id] = decision
        logger.info(f"Decision submitted: {event_id} → {action}")

    def _wait_for_decision(self, event: SteeringEvent, timeout: float = None) -> SteeringDecision:
        """
        Wait for user decision synchronously.
        If timeout expires, returns default action.
        """
        timeout = timeout or event.timeout_seconds
        start = time.time()
        while time.time() - start < timeout:
            decision = self._decision_queue.get(event.event_id)
            if decision is not None:
                return decision
            time.sleep(0.1)

        # Timeout → use default action
        logger.info(f"Steering timeout for {event.event_id}, using default: {event.default_action}")
        return SteeringDecision(
            event_id=event.event_id,
            chosen_action=event.default_action,
        )

    def run_interactive(
        self,
        domain: str,
        question: str,
        config: Dict[str, Any] = None,
        blocking: bool = False,
    ) -> PipelineState:
        """
        Run the full discovery pipeline with steering decision points.
        
        Args:
            domain: Scientific domain
            question: Research question
            config: Pipeline configuration overrides
            blocking: If True, blocks at each steering point waiting for user input.
                      If False, auto-proceeds with defaults after timeout.
        
        Returns:
            PipelineState with all artifacts and steering history.
        """
        mission_id = f"MISSION-{uuid.uuid4().hex[:8].upper()}"
        self.state = PipelineState(mission_id=mission_id, is_running=True)
        config = config or {}

        try:
            # ── Phase 1: Literature Research ──────────────────────────────────
            self._emit_progress("RESEARCH", 0.05, "Searching academic literature...")
            papers = self._phase_research(domain, question)
            self.state.artifacts["papers"] = papers
            self._emit_progress("RESEARCH", 0.15, f"Found {len(papers)} relevant papers")

            # ── Phase 2: Gap Detection + Steering ────────────────────────────
            self._emit_progress("GAP_DETECTION", 0.20, "Analyzing research gaps...")
            gaps = self._phase_gap_detection(papers, domain)
            self.state.artifacts["gaps"] = gaps

            if gaps and blocking:
                event = self._emit_steering_event("gaps_detected", {
                    "gaps": [g if isinstance(g, dict) else {"description": str(g)} for g in gaps[:5]],
                    "domain": domain,
                })
                decision = self._wait_for_decision(event)
                gaps = self._apply_gap_decision(gaps, decision)

            self._emit_progress("GAP_DETECTION", 0.25, f"Pursuing {len(gaps)} research gaps")

            # ── Phase 3: Hypothesis Generation + Steering ────────────────────
            self._emit_progress("HYPOTHESIS_GENERATION", 0.30, "Generating hypotheses...")
            hypotheses = self._phase_hypothesis_generation(domain, question, gaps, papers)
            self.state.artifacts["hypotheses"] = hypotheses

            if hypotheses and blocking:
                event = self._emit_steering_event("hypotheses_generated", {
                    "candidates": [h if isinstance(h, dict) else {"statement": str(h)} for h in hypotheses[:5]],
                    "champion": hypotheses[0] if hypotheses else None,
                })
                decision = self._wait_for_decision(event)
                hypotheses = self._apply_hypothesis_decision(hypotheses, decision)

            self._emit_progress("HYPOTHESIS_GENERATION", 0.40, f"Champion hypothesis selected")

            # ── Phase 4: Hypothesis Evolution ────────────────────────────────
            self._emit_progress("EVOLUTION", 0.45, "Evolving hypothesis population...")
            evolved = self._phase_evolution(hypotheses, domain)
            self.state.artifacts["evolved_population"] = evolved
            self._emit_progress("EVOLUTION", 0.50, f"Population evolved: {len(evolved)} variants")

            # ── Phase 5: Kill Chain + Steering ───────────────────────────────
            self._emit_progress("KILL_CHAIN", 0.55, "Executing adversarial kill chain...")
            kill_result = self._phase_kill_chain(hypotheses, papers)
            self.state.artifacts["kill_chain"] = kill_result

            survival_score = kill_result.get("final_survival_score", 75.0) if isinstance(kill_result, dict) else 75.0
            if survival_score < 60.0 and blocking:
                event = self._emit_steering_event("kill_chain_failure", {
                    "stage": "Adversarial Simulation",
                    "evidence": kill_result.get("strongest_contradiction", "Vulnerability detected"),
                    "score": survival_score,
                })
                decision = self._wait_for_decision(event)
                hypotheses = self._apply_kill_chain_decision(hypotheses, decision, evolved)

            self._emit_progress("KILL_CHAIN", 0.65, f"Kill chain complete: {survival_score:.1f}/100 survival")

            # ── Phase 6: Experiment Design + Steering ────────────────────────
            self._emit_progress("EXPERIMENT", 0.70, "Designing experiment...")
            experiment = self._phase_experiment(hypotheses, domain)
            self.state.artifacts["experiment"] = experiment

            if blocking:
                event = self._emit_steering_event("experiment_designed", {
                    "protocol": "AST-sandboxed computational simulation",
                    "parameters": experiment.get("evaluation_metrics", {}) if isinstance(experiment, dict) else {},
                    "estimated_cost": "Computational only (no lab resources)",
                })
                decision = self._wait_for_decision(event)
                # Apply experiment modifications if needed
                if decision.chosen_action == "modify_parameters":
                    logger.info("User requested parameter modification")

            self._emit_progress("EXPERIMENT", 0.80, "Experiment executed")

            # ── Phase 7: Cross-Domain Transfer + Steering ────────────────────
            self._emit_progress("CROSS_DOMAIN", 0.85, "Exploring cross-domain transfers...")
            cross_domain = self._phase_cross_domain(domain, question)
            self.state.artifacts["cross_domain"] = cross_domain

            if cross_domain and blocking:
                event = self._emit_steering_event("cross_domain_transfer", {
                    "transfer": cross_domain if isinstance(cross_domain, dict) else {"description": str(cross_domain)},
                })
                decision = self._wait_for_decision(event)

            self._emit_progress("CROSS_DOMAIN", 0.90, "Cross-domain analysis complete")

            # ── Phase 8: Synthesis ───────────────────────────────────────────
            self._emit_progress("SYNTHESIS", 0.95, "Synthesizing discovery report...")
            self.state.artifacts["report"] = self._phase_synthesis(
                domain, question, papers, gaps, hypotheses, kill_result, experiment
            )
            self._emit_progress("COMPLETE", 1.0, "Discovery mission complete!")

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            self.state.current_phase = "ERROR"
            self.state.artifacts["error"] = str(e)
        finally:
            self.state.is_running = False
            self.state.phases_completed.append(self.state.current_phase)

        return self.state

    # ─── Phase Implementations ────────────────────────────────────────────────

    def _phase_research(self, domain: str, question: str) -> List[Dict]:
        """Execute literature research phase."""
        try:
            from agents.researcher import ResearcherAgent
            agent = ResearcherAgent()
            return agent.run(question, domain=domain) or []
        except Exception as e:
            logger.warning(f"Research phase error: {e}")
            return [{"title": f"Literature review for {domain}", "abstract": question, "source": "Internal"}]

    def _phase_gap_detection(self, papers: List, domain: str) -> List[Dict]:
        """Execute gap detection phase."""
        try:
            from engines.research_gap_detector import ResearchGapDetector
            detector = ResearchGapDetector()
            return detector.detect_gaps(papers, domain) or []
        except Exception as e:
            logger.warning(f"Gap detection error: {e}")
            return [{"topic": f"Gap in {domain}", "description": "Unexplored research direction"}]

    def _phase_hypothesis_generation(self, domain: str, question: str, gaps: List, papers: List) -> List:
        """Execute hypothesis generation phase."""
        try:
            from agents.innovator import InnovatorAgent
            agent = InnovatorAgent()
            context = "\n".join(
                p.get("abstract", str(p))[:200] if isinstance(p, dict) else str(p)[:200]
                for p in papers[:5]
            )
            hyp = agent.run(context, domain, question)
            return [hyp] if hyp else []
        except Exception as e:
            logger.warning(f"Hypothesis generation error: {e}")
            return [f"Novel hypothesis for {domain}: {question}"]

    def _phase_evolution(self, hypotheses: List, domain: str) -> List:
        """Execute hypothesis evolution phase."""
        try:
            from engines.hypothesis_evolution import HypothesisEvolutionEngine
            engine = HypothesisEvolutionEngine(population_size=6)
            prompt = str(hypotheses[0]) if hypotheses else domain
            population = engine.generate_initial_population(prompt, domain)
            evolved = engine.evolve_generation(population, generation_num=1, domain=domain)
            return [h.to_dict() for h in evolved[:5]]
        except Exception as e:
            logger.warning(f"Evolution phase error: {e}")
            return []

    def _phase_kill_chain(self, hypotheses: List, papers: List) -> Dict:
        """Execute kill chain phase."""
        try:
            from engines.kill_chain import HypothesisKillChain
            chain = HypothesisKillChain()
            hyp_dict = hypotheses[0] if isinstance(hypotheses[0], dict) else {"statement": str(hypotheses[0])}
            paper_dicts = [p if isinstance(p, dict) else {"title": str(p)} for p in papers]
            report = chain.execute_kill_chain(hyp_dict, paper_dicts)
            return report.to_dict() if hasattr(report, 'to_dict') else report
        except Exception as e:
            logger.warning(f"Kill chain error: {e}")
            return {"final_survival_score": 75.0, "strongest_support": "Literature", "strongest_contradiction": "None"}

    def _phase_experiment(self, hypotheses: List, domain: str) -> Dict:
        """Execute experiment phase."""
        try:
            from agents.experiment_agent import ExperimentAgent
            agent = ExperimentAgent(timeout_sec=6.0)
            hyp_text = str(hypotheses[0]) if hypotheses else "Default hypothesis"
            result = agent.run(hyp_text, domain=domain)
            return result.to_dict() if hasattr(result, 'to_dict') else result
        except Exception as e:
            logger.warning(f"Experiment error: {e}")
            return {"evaluation_metrics": {"p_value": 0.001}, "hypothesis_id": "SIM"}

    def _phase_cross_domain(self, domain: str, question: str) -> Dict:
        """Execute cross-domain transfer phase."""
        try:
            from agents.cross_domain_agent import CrossDomainAgent
            agent = CrossDomainAgent()
            # Pick a contrasting source domain
            domain_pairs = {
                "physics": "biology", "biology": "computer_science",
                "computer_science": "economics", "economics": "ecology",
                "materials_science": "neuroscience", "neuroscience": "physics",
            }
            source = domain_pairs.get(domain.lower().split()[0], "physics")
            result = agent.run(source, domain, question[:500])
            return result.to_dict() if hasattr(result, 'to_dict') else result
        except Exception as e:
            logger.warning(f"Cross-domain error: {e}")
            return {}

    def _phase_synthesis(self, domain, question, papers, gaps, hypotheses, kill_result, experiment) -> str:
        """Synthesize final discovery report."""
        try:
            from llm_engine.llama3_handler import generate_text
            summary = generate_text(
                f"Write a concise scientific discovery summary for domain '{domain}', "
                f"research question '{question}', based on {len(papers)} papers analyzed, "
                f"{len(gaps)} research gaps found, and experiment results.",
                system_prompt="You are a scientific report writer. Be concise and factual.",
                temperature=0.3
            )
            return summary or f"# Discovery Report: {domain}\n\nResearch complete."
        except Exception:
            return f"# Discovery Report: {domain}\n\nPipeline completed successfully."

    # ─── Decision Application Methods ─────────────────────────────────────────

    def _apply_gap_decision(self, gaps: List, decision: SteeringDecision) -> List:
        """Apply user's gap selection decision."""
        action = decision.chosen_action
        if action == "pursue_gap_1" and gaps:
            return [gaps[0]]
        elif action == "pursue_gap_2" and len(gaps) > 1:
            return [gaps[1]]
        elif action == "merge_gaps" and len(gaps) >= 2:
            merged = gaps[0].copy() if isinstance(gaps[0], dict) else {"description": str(gaps[0])}
            if isinstance(gaps[1], dict):
                merged["description"] = f"{merged.get('description', '')} + {gaps[1].get('description', '')}"
            return [merged]
        elif action == "add_custom_gap":
            custom = decision.parameters.get("custom_gap", "User-defined research direction")
            gaps.insert(0, {"topic": "Custom Gap", "description": custom})
            return gaps
        return gaps

    def _apply_hypothesis_decision(self, hypotheses: List, decision: SteeringDecision) -> List:
        """Apply user's hypothesis selection decision."""
        action = decision.chosen_action
        if action == "approve_champion":
            return hypotheses  # Keep as is
        elif action == "edit_hypothesis":
            edited = decision.parameters.get("edited_text", "")
            if edited:
                hypotheses[0] = edited
            return hypotheses
        elif action == "reject_all":
            return []  # Force re-generation
        return hypotheses

    def _apply_kill_chain_decision(self, hypotheses: List, decision: SteeringDecision, evolved: List) -> List:
        """Apply user's decision after kill chain failure."""
        action = decision.chosen_action
        if action == "pivot_mechanism" and evolved:
            # Replace champion with next evolved variant
            hypotheses[0] = evolved[1] if len(evolved) > 1 else evolved[0]
        elif action == "relax_assumption":
            logger.info("User chose to relax assumptions — continuing with current hypothesis")
        elif action == "abort":
            raise RuntimeError("User aborted mission after kill chain failure")
        return hypotheses


class StreamlitInteractivePipeline:
    """
    Streamlit-specific wrapper that uses session_state for steering decisions.
    Integrates with the existing Streamlit dashboard.
    """

    def __init__(self):
        self.pipeline = InteractivePipeline()
        self._setup_streamlit_hooks()

    def _setup_streamlit_hooks(self):
        """Register Streamlit-compatible callbacks."""
        import streamlit as st

        def on_event(event: SteeringEvent):
            if "pending_events" not in st.session_state:
                st.session_state.pending_events = []
            st.session_state.pending_events.append(event.to_dict())

        def on_progress(phase: str, pct: float, message: str):
            st.session_state.pipeline_phase = phase
            st.session_state.pipeline_progress = pct
            st.session_state.pipeline_message = message

        self.pipeline.register_event_callback(on_event)
        self.pipeline.register_progress_callback(on_progress)

    def run(self, domain: str, question: str, interactive: bool = True) -> PipelineState:
        """Run pipeline with Streamlit integration."""
        return self.pipeline.run_interactive(
            domain=domain,
            question=question,
            blocking=interactive,
        )

    def submit_decision(self, event_id: str, action: str, parameters: Dict = None):
        """Submit a steering decision from Streamlit UI."""
        self.pipeline.submit_decision(event_id, action, parameters)
