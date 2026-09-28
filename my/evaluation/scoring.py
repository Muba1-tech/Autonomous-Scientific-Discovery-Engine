from llm_engine.router import smart_route_prompt
import json
import re

class ScoringEngine:
    def score(self, hypothesis, simulation_result, validation_result):
        print("[Scorer] Evaluating Hypothesis dynamically...")
        prompt = f"Evaluate this scientific hypothesis based on 'innovation' (0.0-1.0) and 'risk' (0.0-1.0). Output strictly a JSON object with these two keys.\nHypothesis: {hypothesis[:1000]}"
        response = smart_route_prompt(prompt, temperature=0.1)
        
        innovation = 0.5
        risk = 0.5
        try:
            match = re.search(r'\{.*\}', response.strip(), re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                innovation = float(data.get('innovation', 0.5))
                risk = float(data.get('risk', 0.5))
        except Exception as e:
            print(f"[Scorer] JSON Parse Error: {e}")
            
        feasibility = simulation_result.get("simulated_feasibility", 0.0)
        causal_validity = 1.0 if validation_result.get("causal_valid") else 0.0
        
        # Bound adjustments based on deterministic neuro-symbolic logic
        if not validation_result.get("symbolic_valid"):
            risk = max(risk, 0.8)
            
        total_score = (innovation + feasibility + causal_validity - risk) / 3.0
        
        # Novelty: Calculate Information Theoretic Epistemic Uncertainty
        # High innovation + High risk = High uncertainty. High causal validity lowers uncertainty.
        epistemic_uncertainty = max(0.01, min(0.99, (innovation * 0.5) + (risk * 0.4) - (causal_validity * 0.3)))
        
        return {
            "innovation": innovation,
            "feasibility": feasibility,
            "risk": risk,
            "causal_validity": causal_validity,
            "epistemic_uncertainty": round(epistemic_uncertainty, 3),
            "total_score": round(max(0, total_score), 2)
        }
