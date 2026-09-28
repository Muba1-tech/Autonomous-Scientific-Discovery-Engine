from llm_engine.llama3_handler import generate_text

class AnalystAgent:
    def run(self, papers, research_goal, stream_callback=None):
        print("[Analyst] Extracting and analyzing content...")
        analyzed_data = []
        for p in papers:
            title = p.get('title', '')
            abstract = p.get('abstract', '')
            # Removed [:150] truncation to allow full chunk ingestion for large PDFs
            analyzed_data.append(f"Title: {title}. Content: {abstract}")
            
        context = "\n---\n".join(analyzed_data)
        print("[Analyst] Identifying research gaps via LLaMA3...")
        gaps_prompt = f"Research Goal / Question: {research_goal}\n\nAnalyze the following research context accurately. Identify 2-3 specific research gaps, limitations, or methodological inconsistencies directly related to the user's goal. CRITICAL: Be factually correct, strictly base your analysis ONLY on the provided context, and DO NOT hallucinate external information. Explicitly mention the papers (e.g., 'The study on X...') when stating limitations.\n\nFORMAT REQUIREMENT: Output your response strictly as a clean, bulleted Markdown list.\n\nContext: {context}"
        
        system_role = "You are a meticulous, highly critical Lead Research Analyst with expertise spanning all fields of human knowledge. Your job is to extract factual data and relentlessly identify methodological flaws or research gaps across any domain without hallucinating."
        gaps = generate_text(gaps_prompt, system_prompt=system_role, temperature=0.1, stream_callback=stream_callback)
        
        return context, gaps
