from llm_engine.llama3_handler import generate_text

class InnovatorAgent:
    def run(self, context, domain_goal, research_goal, past_knowledge=None, stream_callback=None, expert_disciplines=None):
        print("[Innovator] Synthesizing first-principles novel hypothesis...")
        
        evolution_prompt = ""
        if past_knowledge and len(past_knowledge) > 0:
            evolution_prompt = "\n\n[Prior Knowledge Context]:\n" + "\n".join([f"- {k[:250]}..." for k in past_knowledge[:3]])
            
        disciplines_str = ", ".join(expert_disciplines) if expert_disciplines else "Multidisciplinary Science"
            
        prompt = (
            f"Scientific Field: {domain_goal}\n"
            f"Research Question / Target: {research_goal}\n"
            f"Expert Disciplines: {disciplines_str}\n\n"
            f"Retrieved Academic Context:\n{context[:3000]}{evolution_prompt}\n\n"
            f"Task: Formulate a rigorous, groundbreaking, testable scientific hypothesis that addresses the Research Question.\n"
            f"Requirements:\n"
            f"1. Ground all claims strictly in fundamental scientific laws and the retrieved context.\n"
            f"2. Clearly state the causal mechanism and proposed methodology.\n"
            f"3. Be concise — no filler, no verbose derivations, no lengthy preambles.\n\n"
            f"Output Format (follow EXACTLY — no extra sections):\n"
            f"### Novel Hypothesis\n[One clear, testable, falsifiable hypothesis statement in 2-3 sentences max]\n\n"
            f"### Abstract\n[A concise 3-4 sentence abstract covering: the problem, proposed mechanism, and expected impact]"
        )
        
        system_role = f"You are a Senior Principal Scientist specializing in {disciplines_str}. Your answers are mathematically precise, factually accurate, and derived strictly from first principles."
        return generate_text(prompt, system_prompt=system_role, temperature=0.3, stream_callback=stream_callback)
