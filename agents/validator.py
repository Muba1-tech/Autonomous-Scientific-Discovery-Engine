from llm_engine.deepseek_handler import analyze_text
from neuro_symbolic.symbolic_reasoner import SymbolicReasoner
from causal_engine.causal_model import CausalModel
from causal_engine.inference import CausalInference

class ValidatorAgent:
    def __init__(self):
        self.reasoner = SymbolicReasoner()
        self.causal_model = CausalModel()
        self.causal_inference = CausalInference(self.causal_model)

    def run(self, hypothesis, critique):
        print("[Validator] Validating with DeepSeek + Neuro-Symbolic + Causal Logic...")
        
        # 1. LLM Validation
        system_role = "You are a precise, incorruptible AI Validator. Your job is to strictly evaluate the scientific validity of a hypothesis against a given critique. Be extremely concise and factual in your evaluation."
        llm_val = analyze_text(f"Evaluate if this hypothesis is factually correct, logically sound, free of hallucinations, and survives the critique. Provide a definitive and scientifically accurate evaluation. H: {hypothesis} C: {critique}", system_prompt=system_role, temperature=0.1)
        
        # 2. Symbolic logic check
        sym_result = self.reasoner.reason(hypothesis, risk_score=0.4)
        
        # 3. Causal check
        self.causal_model.build_from_text(["Hypothesis Foundation", "Experimental Factor", "Expected Outcome"])
        causal_valid = self.causal_inference.check_path("Hypothesis Foundation", "Expected Outcome")
        
        return {
            "llm_validation": llm_val,
            "symbolic_valid": sym_result["symbolic_validity"],
            "causal_valid": causal_valid,
            "final_verdict": "Approved" if (sym_result["symbolic_validity"] and causal_valid) else "Rejected"
        }
