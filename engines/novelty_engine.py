import numpy as np
from typing import List, Dict, Any, Optional
from rag_engine.embeddings import EmbeddingEngine
from database.models import NoveltyScores
from config import Config

class NoveltyEngine:
    """
    Multi-Signal Novelty & Priority Scoring Engine for PROJECT AION.
    Uses multi-dimensional semantic vector distance, cross-domain concept isolation, 
    and evidence strength calculations instead of simple prompt querying.
    """
    def __init__(self):
        self.embedder = EmbeddingEngine()

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def evaluate_hypothesis(
        self,
        hypothesis: str,
        papers: List[Dict[str, Any]],
        past_hypotheses: Optional[List[str]] = None,
        gaps: Optional[List[Any]] = None,
        simulated_feasibility: float = 0.5,
        weights: Optional[Dict[str, float]] = None
    ) -> NoveltyScores:
        """
        Evaluates a hypothesis using 5 explicit mathematical signals.
        Returns a NoveltyScores dataclass containing 0-100 metrics.
        """
        if not weights:
            weights = {
                "novelty": Config.WEIGHT_NOVELTY,
                "feasibility": Config.WEIGHT_FEASIBILITY,
                "impact": Config.WEIGHT_IMPACT,
                "evidence": Config.WEIGHT_EVIDENCE
            }

        # 1. Semantic Embeddings Generation
        hyp_emb = self.embedder.generate_embeddings([hypothesis])[0]
        
        # Signal 1: Paper Overlap / Uniqueness (Inverse of Max Similarity with Existing Literature)
        paper_sims = []
        for p in papers:
            p_text = f"{p.get('title', '')} {p.get('abstract', '')}"
            if p_text.strip():
                p_emb = self.embedder.generate_embeddings([p_text])[0]
                sims = self._cosine_similarity(hyp_emb, p_emb)
                paper_sims.append(sims)

        max_paper_sim = max(paper_sims) if paper_sims else 0.5
        avg_paper_sim = float(np.mean(paper_sims)) if paper_sims else 0.5
        # High paper similarity reduces novelty (0 to 100)
        paper_uniqueness_score = (1.0 - max_paper_sim) * 100.0

        # Signal 2: Evolutionary Memory Distance (Uniqueness compared to past runs)
        past_sims = []
        if past_hypotheses:
            for ph in past_hypotheses:
                if ph and ph.strip():
                    ph_emb = self.embedder.generate_embeddings([ph])[0]
                    past_sims.append(self._cosine_similarity(hyp_emb, ph_emb))
        max_past_sim = max(past_sims) if past_sims else 0.2
        memory_uniqueness_score = (1.0 - max_past_sim) * 100.0

        # Signal 3: Concept Combination Novelty (Detecting cross-domain / radical key terms)
        radical_terms = ['cross-domain', 'analogy', 'quantum', 'biomimicry', 'thermodynamic', 'first principles', 'epigenetic', 'synergistic']
        term_count = sum(1 for term in radical_terms if term in hypothesis.lower())
        concept_novelty_bonus = min(25.0, term_count * 5.0)

        # Composite Novelty Score (0 - 100)
        raw_novelty = (paper_uniqueness_score * 0.6) + (memory_uniqueness_score * 0.3) + concept_novelty_bonus
        novelty_score = max(5.0, min(99.0, raw_novelty))

        # 2. Feasibility Score (0 - 100)
        # Combines sandbox execution result (0.0 - 1.0) with text complexity checks
        feasibility_score = max(5.0, min(99.0, simulated_feasibility * 100.0))

        # 3. Potential Impact Score (0 - 100)
        # Higher if addresses multiple research gaps or contains breakthrough key phrases
        gap_relevance = min(40.0, len(gaps) * 15.0) if gaps else 15.0
        impact_terms = ['paradigm shift', 'breakthrough', 'exponential', 'scalable', 'transformative', 'universal']
        impact_term_score = sum(10.0 for t in impact_terms if t in hypothesis.lower())
        potential_impact_score = max(10.0, min(99.0, 40.0 + gap_relevance + impact_term_score))

        # 4. Evidence Strength (0 - 100)
        # Based on average similarity to top retrieved literature chunks (verifiability)
        evidence_strength = max(10.0, min(99.0, avg_paper_sim * 100.0 + 20.0))

        # 5. Overall Research Priority Score (Transparent Weighted Formula)
        priority_score = (
            (novelty_score * weights["novelty"]) +
            (feasibility_score * weights["feasibility"]) +
            (potential_impact_score * weights["impact"]) +
            (evidence_strength * weights["evidence"])
        )

        return NoveltyScores(
            novelty_score=round(novelty_score, 2),
            feasibility_score=round(feasibility_score, 2),
            potential_impact_score=round(potential_impact_score, 2),
            evidence_strength=round(evidence_strength, 2),
            priority_score=round(priority_score, 2),
            sub_metrics={
                "paper_uniqueness": round(paper_uniqueness_score, 2),
                "memory_uniqueness": round(memory_uniqueness_score, 2),
                "max_paper_similarity": round(max_paper_sim, 3),
                "avg_paper_similarity": round(avg_paper_sim, 3)
            }
        )
