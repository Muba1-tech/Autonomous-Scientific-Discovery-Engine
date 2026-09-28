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
            web_context = "\n[WEB SEARCH]: Disabled in TURBO_MODE. Using literature evidence only.\n"
        else:
            try:
                if stream_callback:
                    stream_callback("🌐 Running Live Web Search Fact-Check...\n")
                keywords = hypothesis[:100].replace('\n', ' ')
                
                if os.environ.get("WEB_SEARCH_ENABLED") == "1" and os.environ.get("TAVILY_API_KEY"):
                    tavily_url = "https://api.tavily.com/search"
                    payload = {"api_key": os.environ.get("TAVILY_API_KEY"), "query": keywords, "search_depth": "basic", "max_results": 3}
                    res = requests.post(tavily_url, json=payload, timeout=2.0)
                    if res.status_code == 200:
                        results = res.json().get("results", [])
                        snippets = [r.get("content", "") for r in results]
                        if snippets:
                            web_context = "\n[LIVE WEB CONTEXT]:\n" + "\n".join(f"- {s}" for s in snippets)
                
                if not web_context:
                    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(keywords)}"
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    res = requests.get(url, headers=headers, timeout=2.0)
                    if res.status_code == 200:
                        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', res.text, re.IGNORECASE | re.DOTALL)
                        if snippets:
                            clean_snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:3]]
                            web_context = "\n[LIVE WEB CONTEXT]:\n" + "\n".join(f"- {s}" for s in clean_snippets)
            except Exception:
                pass
                
            if not web_context:
                web_context = "\n[LIVE WEB CONTEXT]: No recent web data found. Using literature evidence only.\n"
                
        prompt = f"Critique this hypothesis for factual accuracy, logical consistency, and potential flaws or risks. Identify any incorrect assumptions, hallucinations, or physically/logically impossible claims: {hypothesis}\n\nUse this live web data to ground your critique: {web_context}\n\nFORMAT REQUIREMENT: Output your response strictly as a Markdown table with two columns: 'Pros (Strengths)' and 'Cons (Flaws/Risks)'."
        
        system_role = "You are a ruthless, highly logical peer-reviewer with expertise spanning all fields of human knowledge. Your sole purpose is to factually evaluate cross-domain hypotheses, finding fatal flaws, biases, and logical fallacies using live web search context. You strictly format your critiques in structured markdown tables."
        return analyze_text(prompt, system_prompt=system_role, temperature=0.2, stream_callback=stream_callback)
