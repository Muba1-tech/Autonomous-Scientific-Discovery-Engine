import re
import json
from typing import Dict, Any, List, Tuple
from llm_engine.router import smart_route_prompt
from config import Config

class SelfCorrectionEngine:
    """
    Hypothesis Self-Correction Engine for PROJECT AION.
    Executes a 5-layer validation check:
    - Layer 1: Logical consistency
    - Layer 2: Evidence consistency
    - Layer 3: Knowledge graph consistency
    - Layer 4: Mathematical / Constraint validation
    - Layer 5: Research feasibility
    Iteratively refines the hypothesis if issues are detected up to max_iterations.
    """
    def __init__(self, max_iterations: int = None):
        self.max_iterations = max_iterations or Config.MAX_CORRECTION_ITERATIONS

    def validate_layers(self, hypothesis: str, context: str) -> Tuple[bool, List[str]]:
        """
        Runs all 5 validation layers against the hypothesis.
        Returns (is_valid, list_of_detected_issues).
        """
        issues = []
        prompt = (
            f"Perform a strict 5-layer scientific sanity audit on this hypothesis:\n\n"
            f"Hypothesis:\n{hypothesis[:2000]}\n\n"
            f"Context Evidence:\n{context[:1500]}\n\n"
            "Audit across these 5 layers:\n"
            "Layer 1: Logical consistency (Does it contradict itself?)\n"
            "Layer 2: Evidence consistency (Do stated assumptions align with context?)\n"
            "Layer 3: Knowledge consistency (Are causal entity relations valid?)\n"
            "Layer 4: Mathematical/Constraint validation (Are equations/formulas physically impossible?)\n"
            "Layer 5: Research feasibility (Is it practically testable?)\n\n"
            "Output strictly a JSON object with schema:\n"
            "{\n"
            "  \"is_valid\": true/false,\n"
            "  \"issues\": [\"Issue 1 description if any\"]\n"
            "}\n"
            "Strictly return JSON."
        )

        response = smart_route_prompt(prompt, temperature=0.1)
        try:
            match = re.search(r'\{.*\}', response.strip(), re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return data.get("is_valid", True), data.get("issues", [])
        except Exception:
            pass

        return True, []

    def self_correct(self, hypothesis: str, context: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Iteratively validates and self-corrects the hypothesis.
        Returns (final_corrected_hypothesis, iteration_audit_logs).
        """
        current_hypothesis = hypothesis
        audit_logs = []

        for iteration in range(1, self.max_iterations + 1):
            is_valid, issues = self.validate_layers(current_hypothesis, context)
            
            audit_logs.append({
                "iteration": iteration,
                "is_valid": is_valid,
                "issues": issues,
                "hypothesis_snapshot": current_hypothesis[:300] + "..."
            })

            if is_valid or not issues:
                print(f"[SelfCorrectionEngine] [OK] Hypothesis passed 5-layer validation on iteration {iteration}.")
                break

            print(f"[SelfCorrectionEngine] [WARN] Layer violations detected on iteration {iteration}: {issues}. Correcting...")
            
            # Refine hypothesis based on identified issues
            refine_prompt = (
                f"Your research hypothesis has been flagged with the following scientific issues:\n"
                + "\n".join([f"- {iss}" for iss in issues]) + "\n\n"
                f"Original Hypothesis:\n{current_hypothesis}\n\n"
                f"Context Evidence:\n{context[:1500]}\n\n"
                "Modify and rewrite the hypothesis to eliminate all flagged logical, mathematical, or empirical inconsistencies.\n"
                "Maintain extreme scientific accuracy and LaTeX formulas where relevant.\n"
                "Output ONLY the corrected, upgraded Markdown hypothesis."
            )

            current_hypothesis = smart_route_prompt(refine_prompt, temperature=0.3)

        return current_hypothesis, audit_logs
