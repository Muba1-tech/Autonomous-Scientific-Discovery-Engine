"""Research mode configurations for PROJECT AION.

Each mode controls which agents are activated, budget limits,
hypothesis population sizes, and investigation depth.
"""
import enum
from dataclasses import dataclass, field
from typing import List, Dict, Any


class ResearchMode(enum.Enum):
    """Available research investigation modes."""
    QUICK = 'QUICK'
    DEEP_RESEARCH = 'DEEP_RESEARCH'
    AUTONOMOUS_DISCOVERY = 'AUTONOMOUS_DISCOVERY'
    EXPERIMENTAL = 'EXPERIMENTAL'
    FALSIFICATION = 'FALSIFICATION'
    LITERATURE = 'LITERATURE'
    DATA_SCIENCE = 'DATA_SCIENCE'

    @property
    def display_name(self) -> str:
        return self.value.replace('_', ' ').title()

    @property
    def description(self) -> str:
        descriptions = {
            'QUICK': 'Fast answer with limited investigation. Best for quick scoping.',
            'DEEP_RESEARCH': 'Thorough literature and evidence analysis with moderate hypothesis generation.',
            'AUTONOMOUS_DISCOVERY': 'Full multi-agent investigation with evolutionary hypothesis refinement, falsification, and debate.',
            'EXPERIMENTAL': 'Focus on computational experiments and simulation-driven discovery.',
            'FALSIFICATION': 'Focus on trying to disprove existing hypotheses through systematic falsification.',
            'LITERATURE': 'Focus on literature synthesis, gap detection, and evidence mapping.',
            'DATA_SCIENCE': 'Focus on uploaded dataset analysis, statistical testing, and data-driven hypothesis generation.'
        }
        return descriptions.get(self.value, '')


@dataclass
class ModeConfig:
    """Configuration for a specific research mode.

    Controls agent selection, budget allocation, depth of investigation,
    and which pipeline phases are active.
    """
    mode: ResearchMode
    # Literature budgets
    max_papers: int = 20
    max_api_calls: int = 10
    # Hypothesis budgets
    initial_population_size: int = 10
    max_generations: int = 3
    survivors_per_generation: float = 0.5  # Ratio kept each gen
    # Agent budgets
    max_agent_calls: int = 50
    max_concurrent_agents: int = 4
    agent_timeout_seconds: int = 120
    agent_retries: int = 2
    # Phase toggles
    enable_literature_search: bool = True
    enable_evidence_extraction: bool = True
    enable_gap_detection: bool = True
    enable_hypothesis_generation: bool = True
    enable_hypothesis_evolution: bool = False
    enable_falsification: bool = False
    enable_contradiction_hunting: bool = False
    enable_experiments: bool = False
    enable_debate: bool = False
    enable_peer_review: bool = False
    enable_counterfactual: bool = False
    enable_dataset_analysis: bool = False
    # Simulation budgets
    max_simulations: int = 10
    simulation_timeout_seconds: int = 60
    # Time limits
    mission_timeout_hours: float = 1.0
    # Active agent roles for this mode
    active_agents: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict
        d = asdict(self)
        d['mode'] = self.mode.value
        return d


def get_mode_config(mode: ResearchMode) -> ModeConfig:
    """Get the default configuration for a research mode.

    Returns a ModeConfig with sensible defaults for the given mode.
    Users can override individual settings after creation.
    """
    configs = {
        ResearchMode.QUICK: ModeConfig(
            mode=ResearchMode.QUICK,
            max_papers=5,
            max_api_calls=3,
            initial_population_size=3,
            max_generations=1,
            max_agent_calls=15,
            max_concurrent_agents=4,
            agent_timeout_seconds=60,
            agent_retries=1,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=True,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=False,
            enable_falsification=False,
            enable_contradiction_hunting=False,
            enable_experiments=False,
            enable_debate=False,
            enable_peer_review=False,
            enable_counterfactual=False,
            enable_dataset_analysis=False,
            max_simulations=0,
            mission_timeout_hours=0.25,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist', 'NoveltyReviewer']
        ),
        ResearchMode.DEEP_RESEARCH: ModeConfig(
            mode=ResearchMode.DEEP_RESEARCH,
            max_papers=50,
            max_api_calls=15,
            initial_population_size=10,
            max_generations=3,
            survivors_per_generation=0.5,
            max_agent_calls=80,
            max_concurrent_agents=4,
            agent_timeout_seconds=120,
            agent_retries=2,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=True,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=True,
            enable_falsification=True,
            enable_contradiction_hunting=True,
            enable_experiments=True,
            enable_debate=False,
            enable_peer_review=True,
            enable_counterfactual=False,
            enable_dataset_analysis=False,
            max_simulations=20,
            mission_timeout_hours=2.0,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist',
                           'Skeptic', 'ExperimentDesigner', 'SimulationScientist',
                           'Statistician', 'NoveltyReviewer', 'PeerReviewer']
        ),
        ResearchMode.AUTONOMOUS_DISCOVERY: ModeConfig(
            mode=ResearchMode.AUTONOMOUS_DISCOVERY,
            max_papers=200,
            max_api_calls=50,
            initial_population_size=50,
            max_generations=10,
            survivors_per_generation=0.5,
            max_agent_calls=500,
            max_concurrent_agents=6,
            agent_timeout_seconds=180,
            agent_retries=3,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=True,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=True,
            enable_falsification=True,
            enable_contradiction_hunting=True,
            enable_experiments=True,
            enable_debate=True,
            enable_peer_review=True,
            enable_counterfactual=True,
            enable_dataset_analysis=False,
            max_simulations=100,
            mission_timeout_hours=24.0,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist',
                           'Skeptic', 'ExperimentDesigner', 'SimulationScientist',
                           'Statistician', 'NoveltyReviewer', 'PeerReviewer']
        ),
        ResearchMode.EXPERIMENTAL: ModeConfig(
            mode=ResearchMode.EXPERIMENTAL,
            max_papers=20,
            max_api_calls=8,
            initial_population_size=5,
            max_generations=2,
            max_agent_calls=100,
            max_concurrent_agents=4,
            agent_timeout_seconds=180,
            agent_retries=2,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=True,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=False,
            enable_falsification=False,
            enable_contradiction_hunting=False,
            enable_experiments=True,
            enable_debate=False,
            enable_peer_review=False,
            enable_counterfactual=True,
            enable_dataset_analysis=True,
            max_simulations=200,
            simulation_timeout_seconds=120,
            mission_timeout_hours=4.0,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist',
                           'ExperimentDesigner', 'SimulationScientist', 'Statistician']
        ),
        ResearchMode.FALSIFICATION: ModeConfig(
            mode=ResearchMode.FALSIFICATION,
            max_papers=30,
            max_api_calls=12,
            initial_population_size=5,
            max_generations=1,
            max_agent_calls=80,
            max_concurrent_agents=4,
            agent_timeout_seconds=120,
            agent_retries=2,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=True,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=False,
            enable_falsification=True,
            enable_contradiction_hunting=True,
            enable_experiments=True,
            enable_debate=True,
            enable_peer_review=True,
            enable_counterfactual=False,
            enable_dataset_analysis=False,
            max_simulations=50,
            mission_timeout_hours=3.0,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist',
                           'Skeptic', 'ExperimentDesigner', 'SimulationScientist',
                           'Statistician', 'PeerReviewer']
        ),
        ResearchMode.LITERATURE: ModeConfig(
            mode=ResearchMode.LITERATURE,
            max_papers=100,
            max_api_calls=30,
            initial_population_size=5,
            max_generations=1,
            max_agent_calls=60,
            max_concurrent_agents=4,
            agent_timeout_seconds=120,
            agent_retries=2,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=True,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=False,
            enable_falsification=False,
            enable_contradiction_hunting=True,
            enable_experiments=False,
            enable_debate=False,
            enable_peer_review=False,
            enable_counterfactual=False,
            enable_dataset_analysis=False,
            max_simulations=0,
            mission_timeout_hours=2.0,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist',
                           'NoveltyReviewer']
        ),
        ResearchMode.DATA_SCIENCE: ModeConfig(
            mode=ResearchMode.DATA_SCIENCE,
            max_papers=10,
            max_api_calls=5,
            initial_population_size=5,
            max_generations=2,
            max_agent_calls=80,
            max_concurrent_agents=4,
            agent_timeout_seconds=120,
            agent_retries=2,
            enable_literature_search=True,
            enable_evidence_extraction=True,
            enable_gap_detection=False,
            enable_hypothesis_generation=True,
            enable_hypothesis_evolution=False,
            enable_falsification=False,
            enable_contradiction_hunting=False,
            enable_experiments=True,
            enable_debate=False,
            enable_peer_review=False,
            enable_counterfactual=True,
            enable_dataset_analysis=True,
            max_simulations=100,
            simulation_timeout_seconds=120,
            mission_timeout_hours=2.0,
            active_agents=['LiteratureScout', 'EvidenceExtractor', 'HypothesisScientist',
                           'ExperimentDesigner', 'SimulationScientist', 'Statistician']
        )
    }
    return configs.get(mode, configs[ResearchMode.DEEP_RESEARCH])
