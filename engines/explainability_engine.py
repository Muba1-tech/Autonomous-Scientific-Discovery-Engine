import json
from typing import Dict, Any, List, Optional
from llm_engine.router import smart_route_prompt
from database.models import ExplainabilityReport, NoveltyScores

class ExplainabilityEngine:
    """
    Advanced Explainability Engine for PROJECT AION.
    Generates human-readable decision rationale reports ("Why AION Selected This Hypothesis")
    describing key evidence, score breakdowns, gap alignment, and cross-domain links.
    """
    def __init__(self):
        pass

    def generate_report(
        self,
        research_id: str,
        hypothesis_title: str,
        hypothesis_content: str,
        scores: NoveltyScores,
        gaps: List[Any],
        papers: List[Dict[str, Any]],
        past_hypotheses: Optional[List[str]] = None,
        cross_domain_info: Optional[Dict[str, Any]] = None
    ) -> ExplainabilityReport:
        """
        Synthesizes human-readable decision tree explanation.
        """
        gap_titles = [getattr(g, 'topic', str(g)) for g in gaps] if gaps else ["General Domain Advancement"]
        paper_titles = [p.get('title', 'Indexed Paper') for p in papers[:3]] if papers else ["Retrieved Scientific Context"]

        scores_dict = scores.to_dict() if isinstance(scores, NoveltyScores) else scores

        prompt = (
            f"Hypothesis Title: {hypothesis_title}\n"
            f"Hypothesis Content: {hypothesis_content[:1500]}\n\n"
            f"Evaluation Metrics:\n"
            f"- Priority Score: {scores_dict.get('priority_score', 80.0)}/100\n"
            f"- Novelty Score: {scores_dict.get('novelty_score', 85.0)}/100\n"
            f"- Feasibility Score: {scores_dict.get('feasibility_score', 75.0)}/100\n"
            f"- Potential Impact Score: {scores_dict.get('potential_impact_score', 90.0)}/100\n"
            f"- Evidence Strength: {scores_dict.get('evidence_strength', 80.0)}/100\n\n"
            f"Target Research Gaps Addressed:\n" + "\n".join([f"- {gt}" for gt in gap_titles[:3]]) + "\n\n"
            f"Supporting Papers:\n" + "\n".join([f"- {pt}" for pt in paper_titles[:3]]) + "\n\n"
            "Generate a clear, professional, human-readable rationale report explaining WHY AION selected this specific hypothesis over alternative possibilities.\n"
            "Focus strictly on scientific evidence, gap resolution, structural feasibility, and decision factors.\n"
            "DO NOT expose raw LLM system prompts or internal debug chain-of-thought.\n"
            "Format output cleanly as a structured Markdown explanation."
        )

        rationale = smart_route_prompt(prompt, temperature=0.3)

        return ExplainabilityReport(
            research_id=research_id,
            selected_hypothesis_title=hypothesis_title,
            selection_rationale=rationale,
            gaps_involved=gap_titles,
            supporting_papers=paper_titles,
            key_evidence=[f"Evidence matched across {len(paper_titles)} literature papers."],
            novel_concepts=["First Principles Derivation", "Cross-Domain Analogy Synthesis"],
            cross_domain_connections=[cross_domain_info.get("transferred_concept", "N/A")] if cross_domain_info else [],
            scores_breakdown=scores_dict,
            previous_related_hypotheses=past_hypotheses[:3] if past_hypotheses else []
        )
