import urllib.parse

class WriterAgent:
    def run(self, hypothesis, critique, validation, ethical_review=None, papers=None, gaps=None):
        print("[Writer] Compiling final structured report...")
        
        bib_section = "### 📚 Verifiable Bibliography\n"
        if papers:
            for i, p in enumerate(papers, 1):
                source = p.get('source', 'Unknown API')
                title = p.get('title', 'Untitled')
                url = p.get('url', '')
                
                # Fallback to Google Scholar search if URL isn't explicitly provided by the API
                if not url:
                    query = urllib.parse.quote(title)
                    url = f"https://scholar.google.com/scholar?q={query}"
                    
                download_url = url
                if url and "arxiv.org/abs/" in url:
                    download_url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
                    if not download_url.endswith(".pdf"):
                        download_url += ".pdf"
                    
                bib_section += f"{i}. **<a href='{url}' target='_blank' class='premium-link-title'>{title}</a>** (Source: {source} | <a href='{download_url}' target='_blank' class='premium-btn'>📥 View / Download Paper</a>)\n"
        else:
            bib_section += "*No references were integrated during this run.*\n"
            
        gap_section = "### 🕳️ Highlighted Research Gaps\n"
        gap_section += f"{gaps}\n\n" if gaps else "*No specific gaps identified.*\n\n"

        ethics_section = ""
        if ethical_review:
            ethics_section = f"### ⚖️ Ethical & Societal Impact\n{ethical_review}\n\n"

        report = (
            f"# 📜 Autonomous Self-Evolving Omni-Domain Discovery Report\n\n"
            f"{gap_section}"
            f"### 💡 Generated Hypothesis\n{hypothesis}\n\n"
            f"### 🔍 Critique\n{critique}\n\n"
            f"{ethics_section}"
            f"### ✅ Validation Status: **{validation['final_verdict']}**\n"
            f"- **Symbolic Valid**: {validation['symbolic_valid']}\n"
            f"- **Causal Valid**: {validation['causal_valid']}\n"
            f"- **LLM Remarks**: {validation['llm_validation']}\n\n"
            f"---\n"
            f"{bib_section}"
        )
        return report
