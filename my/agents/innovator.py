from llm_engine.llama3_handler import generate_text
import random

class InnovatorAgent:
    def run(self, context, domain_goal, research_goal, past_knowledge=None, stream_callback=None, expert_disciplines=None):
        print("[Innovator] Generating and evolving novel hypothesis via LLaMA3...")
        
        evolution_prompt = ""
        if past_knowledge and len(past_knowledge) > 0:
            evolution_prompt = "\n\n[SYSTEM EVOLUTION]: You may draw abstract inspiration from these past discoveries, BUT YOU MUST apply them strictly to the new domain:\n"
            evolution_prompt += "\n".join([f"- {k[:300]}..." for k in past_knowledge])
            
        # 🚀 ULTRA-NOVELTY INJECTION: Cross-Domain Biomimicry / Physics Analogies
        analogies = [
            "Mycelial fungal network resource routing",
            "Quantum superposition and entanglement",
            "Fluid dynamics of non-Newtonian fluids",
            "Epigenetic cellular memory adaptation",
            "Astrophysical event horizon thermodynamics",
            "Swarm intelligence in ant colonies"
        ]
        forced_analogy = random.choice(analogies)
        
        disciplines_str = ", ".join(expert_disciplines) if expert_disciplines else "General Knowledge"
            
        prompt = (f"Target Domain: {domain_goal}\nSpecific Research Goal / Question: {research_goal}\n\n"
                  f"You are a collaborative swarm of 5 elite experts specializing in: {disciplines_str}.\n"
                  f"Based on this retrieved academic research context: {context}{evolution_prompt}\n\n"
                  f"🔥 PERFECT ANSWER OVERRIDE (First Principles): Before hypothesizing, break the problem down into absolute, undeniable fundamental axioms of the relevant fields (e.g., physics, math, logic, economics, or philosophy). Derive your solution strictly from these axioms to guarantee factual perfection.\n"
                  f"First, directly and correctly answer the Research Goal / Question using ONLY the provided context.\n"
                  f"CRITICAL INSTRUCTION: DO NOT hallucinate, invent data, or make up facts. If a logical step lacks proof, state it as a known unknown.\n"
                  f"Then, generate a highly innovative, novel hypothesis strictly within the Target Domain by synthesizing the perspectives of your 3 disciplines.\n"
                  f"🔥 EXTREME NOVELTY OVERRIDE: You MUST integrate principles from '{forced_analogy}' as a structural or mathematical analogy to solve the problem in the Target Domain in a completely never-before-seen way. Explain the exact translation of mechanisms from the analogy to the domain.\n"
                  f"You MUST strictly ground your hypothesis in the mechanisms described in the papers. Do not introduce external concepts unless explicitly linking them logically to the provided abstracts.\n"
                  f"Ensure all claims are factually accurate, logically sound, and grounded in the context. Provide detailed reasoning.\n\n"
                  f"FORMAT REQUIREMENT:\n"
                  f"Strictly format your response using the following Markdown structure:\n"
                  f"### 📐 First Principles Derivation\n[Break down into fundamental axioms and derive the logic. You MUST express all mathematical models, theorems, and physics equations using strict LaTeX formatting wrapped in $$...$$ block tags.]\n\n"
                  f"### 🎯 Direct Answer\n[Your clear, factual answer here]\n\n"
                  f"### 🚀 Novel Hypothesis (Analogy: {forced_analogy})\n[Your specific hypothesis here]\n\n"
                  f"### 🧠 Detailed Reasoning & Synthesis\n- [{expert_disciplines[0] if expert_disciplines else 'Point 1'} Perspective]\n- [{expert_disciplines[1] if expert_disciplines else 'Point 2'} Perspective]\n- [{expert_disciplines[2] if expert_disciplines else 'Point 3'} Perspective]\n- [{expert_disciplines[3] if len(expert_disciplines)>3 else 'Point 4'} Perspective]\n- [{expert_disciplines[4] if len(expert_disciplines)>4 else 'Point 5'} Perspective]")
        
        system_role = f"You are a polymath swarm intelligence consisting of the world's leading experts in {disciplines_str}. Your answers are derived from first principles, making them logically sound, highly novel, factually flawless, and strictly formatted."
        return generate_text(prompt, system_prompt=system_role, temperature=0.6, stream_callback=stream_callback) # Increased temp to 0.6 for maximum cross-domain creativity
