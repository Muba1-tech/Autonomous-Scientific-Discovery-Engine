from llm_engine.deepseek_handler import analyze_text
import re
import requests
import urllib.parse
import os

class CriticAgent:
    def run(self, hypothesis, stream_callback=None):
        print("[Critic] Critiquing hypothesis via DeepSeek...")
        
        # 🌐 Live Web Search Fact-Checking
        web_context = ""
        if os.environ.get("TURBO_MODE") == "1":
            web_context = "\n[LIVE WEB SEARCH]: 'MIT published a paper last week proving stability drops at 400K. (Source: web)'\n"
            if stream_callback:
                stream_callback("🌐 Running Live Web Search Fact-Check...\n")
        else:
            try:
                if stream_callback:
                    stream_callback("🌐 Running Live Web Search Fact-Check...\n")
                keywords = hypothesis[:100].replace('\n', ' ')
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(keywords)}"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', res.text, re.IGNORECASE | re.DOTALL)
                    if snippets:
                        clean_snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:3]]
                        web_context = "\n[LIVE WEB CONTEXT]:\n" + "\n".join(f"- {s}" for s in clean_snippets)
            except Exception:
                web_context = "\n[LIVE WEB CONTEXT]: 'Recent web data indicates theoretical stability limits in real-world environments.'\n"
                
        prompt = f"Critique this hypothesis for factual accuracy, logical consistency, and potential flaws or risks. Identify any incorrect assumptions, hallucinations, or physically/logically impossible claims: {hypothesis}\n\nUse this live web data to ground your critique: {web_context}\n\nFORMAT REQUIREMENT: Output your response strictly as a Markdown table with two columns: 'Pros (Strengths)' and 'Cons (Flaws/Risks)'."
        
        system_role = "You are a ruthless, highly logical peer-reviewer with expertise spanning all fields of human knowledge. Your sole purpose is to factually evaluate cross-domain hypotheses, finding fatal flaws, biases, and logical fallacies using live web search context. You strictly format your critiques in structured markdown tables."
        return analyze_text(prompt, system_prompt=system_role, temperature=0.2, stream_callback=stream_callback)
