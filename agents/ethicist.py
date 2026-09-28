from llm_engine.llama3_handler import generate_text

class EthicistAgent:
    def run(self, hypothesis, stream_callback=None):
        print("[Ethicist] Evaluating societal and ethical impact...")
        
        prompt = (
            f"Analyze the following scientific hypothesis for potential societal impact, ethical concerns, "
            f"and risks of dual-use or weaponization: {hypothesis}\n\n"
            f"FORMAT REQUIREMENT: Output your response strictly as a concise Markdown bulleted list "
            f"highlighting 'Beneficial Impacts', 'Ethical Risks', and 'Mitigation Strategies'."
        )
        
        system_role = (
            "You are a strict, visionary AI Ethicist and Sociologist. Your role is to scrutinize "
            "scientific discoveries for potential societal harm, philosophical implications, and "
            "long-term consequences on humanity. You provide clear, objective, and unbiased ethical evaluations."
        )
        
        return generate_text(prompt, system_prompt=system_role, temperature=0.3, stream_callback=stream_callback)