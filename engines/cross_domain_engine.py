import json
import logging
import random
import math
from typing import Dict, Any, List
from database.models import CrossDomainHypothesis
from llm_engine.llama3_handler import generate_text

logger = logging.getLogger(__name__)

class CrossDomainEngine:
    """
    Engine for generating cross-domain hypotheses by analogical reasoning.
    Transfers mechanisms from a source domain to a target domain.
    """
    
    MECHANISM_KNOWLEDGE_BASE = {
        "physics": [
            {"name": "Entropy", "description": "Tendency of systems to move toward disorder over time without energy input."},
            {"name": "Resonance", "description": "Amplification of a system's vibration at a specific natural frequency."},
            {"name": "Quantum Entanglement", "description": "State where particles remain connected so that actions on one affect the other instantly."},
            {"name": "Phase Transition", "description": "Transformation of a thermodynamic system from one state of matter to another."},
            {"name": "Symmetry Breaking", "description": "When a system that is symmetric with respect to some translation or rotation crosses a critical point and loses its symmetry."},
            {"name": "Conservation Laws", "description": "Fundamental principle that a certain physical property does not change in the course of time within an isolated system."},
        ],
        "biology": [
            {"name": "Natural Selection", "description": "Differential survival and reproduction of individuals due to differences in phenotype."},
            {"name": "Homeostasis", "description": "State of steady internal, physical, and chemical conditions maintained by living systems."},
            {"name": "Symbiosis", "description": "Any type of a close and long-term biological interaction between two different biological organisms."},
            {"name": "Metabolism", "description": "Set of life-sustaining chemical reactions in organisms."},
            {"name": "Apoptosis", "description": "Programmed cell death that occurs in multicellular organisms."},
            {"name": "Horizontal Gene Transfer", "description": "Movement of genetic material between unicellular and/or multicellular organisms other than by the vertical transmission of DNA from parent to offspring."},
        ],
        "materials_science": [
            {"name": "Crystallization", "description": "Process by which a solid forms, where the atoms or molecules are highly organized into a structure known as a crystal."},
            {"name": "Work Hardening", "description": "Strengthening of a metal or polymer by plastic deformation."},
            {"name": "Self-Healing", "description": "Ability of a material to automatically repair damages to itself without any external diagnosis of the problem or human intervention."},
            {"name": "Piezoelectric Effect", "description": "Ability of certain materials to generate an electric charge in response to applied mechanical stress."},
            {"name": "Superconductivity", "description": "Set of physical properties observed in certain materials where electrical resistance vanishes and magnetic flux fields are expelled."},
            {"name": "Allotropy", "description": "Property of some chemical elements to exist in two or more different forms, in the same physical state."},
        ],
        "computer_science": [
            {"name": "Caching", "description": "Storing data in a temporary storage area to expedite data retrieval."},
            {"name": "Recursion", "description": "Method of solving a problem where the solution depends on solutions to smaller instances of the same problem."},
            {"name": "Garbage Collection", "description": "Form of automatic memory management that reclaims garbage, or memory occupied by objects that are no longer in use."},
            {"name": "Backpropagation", "description": "Algorithm used to calculate derivatives in a neural network to update weights and minimize error."},
            {"name": "Deadlock", "description": "State in which each member of a group is waiting for another member, including itself, to take action."},
            {"name": "Load Balancing", "description": "Process of distributing a set of tasks over a set of resources with the aim of making their overall processing more efficient."},
        ],
        "economics": [
            {"name": "Supply and Demand", "description": "Economic model of price determination in a market."},
            {"name": "Opportunity Cost", "description": "The value of the next-best alternative when a decision is made."},
            {"name": "Diminishing Returns", "description": "Decrease in the marginal output of a production process as the amount of a single factor of production is incrementally increased."},
            {"name": "Network Effects", "description": "Phenomenon by which the value or utility a user derives from a good or service depends on the number of users of compatible products."},
            {"name": "Arbitrage", "description": "Practice of taking advantage of a price difference between two or more markets."},
            {"name": "Moral Hazard", "description": "Situation in which one party gets involved in a risky event knowing that it is protected against the risk and the other party will incur the cost."},
        ],
        "neuroscience": [
            {"name": "Neuroplasticity", "description": "Ability of the brain to change its structure and function in response to experience or damage."},
            {"name": "Synaptic Pruning", "description": "Process of synapse elimination that occurs between early childhood and the onset of puberty."},
            {"name": "Action Potential", "description": "Short-lasting event in which the electrical membrane potential of a cell rapidly rises and falls."},
            {"name": "Lateral Inhibition", "description": "Capacity of an excited neuron to reduce the activity of its neighbors, enhancing contrast in sensory patterns."},
            {"name": "Long-term Potentiation", "description": "Persistent strengthening of synapses based on recent patterns of activity."},
            {"name": "Hebbian Learning", "description": "Mechanism for synaptic plasticity wherein an increase in synaptic efficacy arises from the presynaptic cell's repeated and persistent stimulation of the postsynaptic cell."},
        ],
        "ecology": [
            {"name": "Trophic Cascade", "description": "Powerful indirect interactions that can control entire ecosystems, occurring when a trophic level in a food web is suppressed."},
            {"name": "Ecological Succession", "description": "Process of change in the species structure of an ecological community over time."},
            {"name": "Niche Partitioning", "description": "Process by which competing species use the environment differently in a way that helps them to coexist."},
            {"name": "Keystone Species", "description": "A species on which other species in an ecosystem largely depend, such that if it were removed the ecosystem would change drastically."},
            {"name": "Carrying Capacity", "description": "Maximum population size of a biological species that can be sustained by that specific environment."},
            {"name": "Ecosystem Engineer", "description": "Any organism that creates, significantly modifies, maintains or destroys a habitat."},
        ]
    }

    def __init__(self):
        logger.info("Initializing CrossDomainEngine")

    def _compute_domain_distance(self, source: str, target: str) -> float:
        """
        Computes a heuristic distance between two domains.
        Returns a float between 0.0 and 1.0, where 1.0 means highly distant (novel).
        """
        source = source.lower()
        target = target.lower()
        
        if source == target:
            return 0.0
            
        domain_coordinates = {
            "physics": (10, 10),
            "materials_science": (9, 9),
            "computer_science": (8, 2),
            "biology": (2, 10),
            "neuroscience": (3, 8),
            "ecology": (1, 8),
            "economics": (5, 1)
        }
        
        c_src = domain_coordinates.get(source, (5, 5))
        c_tgt = domain_coordinates.get(target, (5, 5))
        
        dist = math.sqrt((c_src[0] - c_tgt[0])**2 + (c_src[1] - c_tgt[1])**2)
        
        normalized_dist = min(dist / 12.7, 1.0)
        
        return max(0.3, normalized_dist)

    def _retrieve_source_mechanisms(self, domain: str) -> List[Dict[str, str]]:
        """
        Retrieves mechanisms from the knowledge base for a given domain.
        """
        domain_key = domain.lower()
        mechanisms = self.MECHANISM_KNOWLEDGE_BASE.get(domain_key, [])
        if not mechanisms:
            logger.warning(f"Domain '{domain}' not found in knowledge base. Using default mechanisms.")
            mechanisms = [
                {"name": "Feedback Loop", "description": "A system where the output of a process is used as its input."},
                {"name": "Decentralization", "description": "Distribution of functions and powers away from a central location or authority."}
            ]
        return mechanisms

    def _map_mechanism_to_target(self, mechanism: Dict[str, str], source: str, target: str, context: str) -> Dict[str, Any]:
        """
        Uses LLM to perform analogical mapping of a mechanism from source to target domain.
        """
        prompt = (
            f"You are an expert at cross-domain analogical reasoning.\n"
            f"Source Domain: {source}\n"
            f"Target Domain: {target}\n"
            f"Mechanism from Source: '{mechanism['name']}' - {mechanism['description']}\n\n"
            f"Context: {context}\n\n"
            f"Map this mechanism to the target domain. How can the principles of '{mechanism['name']}' "
            f"be applied to solve problems or explain phenomena in {target}?\n\n"
            f"Return a JSON object with the following keys:\n"
            f"- 'transferred_concept': A short name for the new concept in the target domain.\n"
            f"- 'transfer_rationale': Detailed reasoning explaining how the source mechanism logically applies to the target domain.\n"
            f"- 'hypothesis_statement': A clear, testable scientific hypothesis statement based on this mapping.\n"
            f"- 'existing_evidence': Plausible existing evidence or theoretical justification supporting this analogy.\n"
            f"- 'risks': Potential flaws or risks in this analogy.\n"
            f"- 'potential_impact_score': A float between 0.0 and 1.0 indicating the potential scientific impact.\n"
        )
        
        system_prompt = "You are a creative scientific AI. Output ONLY valid, parsable JSON."
        
        try:
            response_text = generate_text(prompt, system_prompt=system_prompt, temperature=0.3)
            
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            return json.loads(response_text.strip())
        except Exception as e:
            logger.error(f"Error mapping mechanism {mechanism['name']} to {target}: {e}")
            return {
                "transferred_concept": f"{mechanism['name']}-like Process",
                "transfer_rationale": f"Applying {mechanism['name']} from {source} to {target} through general structural mapping.",
                "hypothesis_statement": f"If {target} incorporates {mechanism['name']}, then performance/understanding will improve.",
                "existing_evidence": "Analogical inference from source domain success.",
                "risks": "Mapping may be superficial and fail under experimental conditions.",
                "potential_impact_score": 0.5
            }

    def generate_cross_domain_hypothesis(self, source_domain: str, target_domain: str, context: str = "") -> CrossDomainHypothesis:
        """
        Generates a cross-domain hypothesis by mapping mechanisms from a source domain to a target domain.
        """
        logger.info(f"Generating cross-domain hypothesis from {source_domain} to {target_domain}")
        
        novelty_score = self._compute_domain_distance(source_domain, target_domain)
        mechanisms = self._retrieve_source_mechanisms(source_domain)
        
        mechanism = random.choice(mechanisms)
        logger.info(f"Selected mechanism '{mechanism['name']}' for transfer.")
        
        mapping_result = self._map_mechanism_to_target(mechanism, source_domain, target_domain, context)
        
        base_impact = float(mapping_result.get("potential_impact_score", 0.5))
        potential_impact = min(1.0, base_impact * (0.5 + novelty_score))
        
        hypothesis = CrossDomainHypothesis(
            source_domain=source_domain,
            target_domain=target_domain,
            transferred_concept=mapping_result.get("transferred_concept", "Unknown Concept"),
            transfer_rationale=mapping_result.get("transfer_rationale", "Unknown Rationale"),
            hypothesis_statement=mapping_result.get("hypothesis_statement", "Default hypothesis statement"),
            existing_evidence=mapping_result.get("existing_evidence", "No evidence"),
            novelty_score=round(novelty_score, 3),
            potential_impact=round(potential_impact, 3),
            risks=mapping_result.get("risks", "Unknown risks")
        )
        
        logger.info(f"Generated Hypothesis: {hypothesis.transferred_concept}")
        return hypothesis
