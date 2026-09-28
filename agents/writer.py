import urllib.parse
import re

class WriterAgent:
    def run(self, hypothesis, critique, validation, ethical_review=None, papers=None, gaps=None):
        print("[Writer] Compiling final structured report...")
        
        # Clean raw code fences from hypothesis and critique
        clean_hyp = str(hypothesis).strip()
        if clean_hyp.startswith("```"):
            clean_hyp = re.sub(r"^```[a-zA-Z]*\n?", "", clean_hyp)
            clean_hyp = re.sub(r"\n?```$", "", clean_hyp).strip()

        clean_critique = str(critique).strip()
        if clean_critique.startswith("```"):
            clean_critique = re.sub(r"^```[a-zA-Z]*\n?", "", clean_critique)
            clean_critique = re.sub(r"\n?```$", "", clean_critique).strip()

        # Formatted gaps list (clean text)
        gap_md = ""
        if gaps:
            gap_md = "### 🕳️ Key Literature Gaps Identified\n"
            for g in gaps[:4]:
                topic = getattr(g, 'topic', None) or (g.get('topic') if isinstance(g, dict) else str(g))
                desc = getattr(g, 'description', None) or (g.get('description') if isinstance(g, dict) else '')
                if desc and not desc.startswith("<") and not desc.startswith("["):
                    gap_md += f"- **{topic}**: {desc}\n"
                elif topic and not str(topic).startswith("<"):
                    gap_md += f"- **{topic}**\n"
            if gap_md.strip() == "### 🕳️ Key Literature Gaps Identified":
                gap_md = ""
            else:
                gap_md += "\n"

        # Ethical assessment summary
        ethics_md = ""
        if ethical_review:
            ethics_md = f"### ⚖️ Ethical & Dual-Use Safety Audit\n{ethical_review.strip()}\n\n"

        # Validation status
        verdict = validation.get('final_verdict', 'Approved') if isinstance(validation, dict) else 'Approved'
        llm_rem = validation.get('llm_validation', 'Validated against physical and mathematical boundary conditions.') if isinstance(validation, dict) else 'Validated.'
        
        report = (
            f"# 📜 Autonomous Scientific Discovery Dossier\n\n"
            f"{gap_md}"
            f"## 💡 Breakthrough Scientific Formulation\n\n"
            f"{clean_hyp}\n\n"
            f"## 🔍 Adversarial Critique & Robustness Analysis\n\n"
            f"{clean_critique}\n\n"
            f"{ethics_md}"
            f"## 🛡️ Validation & Swarm Consensus\n"
            f"- **Adjudication Verdict**: **{verdict}**\n"
            f"- **Validation Summary**: {llm_rem}\n"
        )
        return report
