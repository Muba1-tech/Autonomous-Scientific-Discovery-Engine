import json
import re
from typing import List, Dict, Any, Optional
from database.db_manager import DBManager
from llm_engine.router import smart_route_prompt

class EvolutionaryMemoryEngine:
    """
    Evolutionary Memory Engine for PROJECT AION.
    Stores past research cycles in SQLite, extracts successful/failed patterns, 
    and synthesizes actionable memory prompts for future runs.
    """
    def __init__(self, db: Optional[DBManager] = None):
        self.db = db or DBManager()

    def record_cycle(
        self,
        research_id: str,
        domain: str,
        hypothesis: str,
        evidence: str,
        methodology: str,
        experiment_result: str,
        outcome: str = "SUCCESS",
        user_feedback: str = "",
        novelty_score: float = 0.0,
        feasibility_score: float = 0.0,
        impact_score: float = 0.0
    ):
        """
        Records a completed research attempt into SQLite and extracts analytical patterns.
        """
        # Extract patterns via LLM analysis
        patterns = self.analyze_attempt_patterns(hypothesis, experiment_result, outcome)
        
        memory_data = {
            "research_id": research_id,
            "domain": domain,
            "hypothesis": hypothesis,
            "evidence": evidence,
            "methodology": methodology,
            "experiment_result": experiment_result,
            "outcome": outcome,
            "user_feedback": user_feedback,
            "novelty_score": novelty_score,
            "feasibility_score": feasibility_score,
            "impact_score": impact_score,
            "patterns_extracted": patterns
        }
        self.db.insert_agent_memory(memory_data)
        print(f"[EvolutionaryMemory] Recorded research cycle {research_id} with outcome: {outcome}")

    def analyze_attempt_patterns(self, hypothesis: str, result: str, outcome: str) -> List[str]:
        """
        Analyzes what worked or failed to extract generalizable research guidelines.
        """
        prompt = (
            f"Analyze this research hypothesis attempt:\n\nHypothesis: {hypothesis[:1000]}\n"
            f"Execution/Simulation Result: {result[:1000]}\nOutcome: {outcome}\n\n"
            "Extract 2 concise, actionable research insights or patterns:\n"
            "1. If SUCCESS: What specific structural or methodological choice contributed to success?\n"
            "2. If FAILURE: What specific pitfall or flaw led to failure?\n"
            "Output strictly a JSON list of 2 strings."
        )
        response = smart_route_prompt(prompt, temperature=0.1)
        try:
            match = re.search(r'\[.*\]', response.strip(), re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return [f"Outcome pattern: {outcome} observed during simulation execution."]

    def get_evolutionary_prompt_context(self, domain: str) -> str:
        """
        Queries historical memory to synthesize guidance for future hypothesis generation.
        """
        memories = self.db.get_agent_memory(domain=domain, limit=10)
        if not memories:
            memories = self.db.get_agent_memory(limit=10)
            
        if not memories:
            return ""

        successful_strategies = []
        failed_pitfalls = []
        explored_directions = []

        for m in memories:
            explored_directions.append(f"- Hypothesis: {m.get('hypothesis', '')[:120]}... (Domain: {m.get('domain', '')})")
            patterns = m.get('patterns_extracted', [])
            if m.get('outcome') == 'SUCCESS':
                for p in patterns:
                    successful_strategies.append(f"- {p}")
            else:
                for p in patterns:
                    failed_pitfalls.append(f"- {p}")

        evolution_text = "\n🧬 [EVOLUTIONARY MEMORY & HISTORICAL INFERENCE]:\n"
        
        if explored_directions:
            evolution_text += "Already Explored Research Directions:\n" + "\n".join(explored_directions[:5]) + "\n\n"
            
        if successful_strategies:
            evolution_text += "Proven Successful Strategies (Emulate these):\n" + "\n".join(set(successful_strategies[:5])) + "\n\n"
            
        if failed_pitfalls:
            evolution_text += "Repeatedly Failed Pitfalls (Avoid these):\n" + "\n".join(set(failed_pitfalls[:5])) + "\n\n"
            
        return evolution_text

    def query_memory_analytics(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Answers structural questions about memory:
        - Which hypotheses worked?
        - Which failed?
        - Which directions were explored?
        """
        memories = self.db.get_agent_memory(domain=domain, limit=50)
        successful = [m for m in memories if m.get('outcome') == 'SUCCESS']
        failed = [m for m in memories if m.get('outcome') != 'SUCCESS']
        
        return {
            "total_attempts": len(memories),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "successful_hypotheses": [m.get('hypothesis', '')[:200] for m in successful[:5]],
            "failed_approaches": [m.get('hypothesis', '')[:200] for m in failed[:5]],
            "explored_directions": [m.get('domain', '') + ": " + m.get('hypothesis', '')[:100] for m in memories[:10]]
        }
