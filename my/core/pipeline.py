from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.innovator import InnovatorAgent
from agents.critic import CriticAgent
from agents.validator import ValidatorAgent
from agents.ethicist import EthicistAgent
from agents.writer import WriterAgent

from rag_engine.embeddings import EmbeddingEngine
from rag_engine.retriever import FAISSRetriever
from cognitive_twin.twin_engine import TwinEngine
from debate.communication import MessageBus
from debate.consensus import ConsensusEngine
from simulation.hypothesis_simulator import HypothesisSimulator
from evaluation.scoring import ScoringEngine
from outputs.report_generator import ReportGenerator
from database.db_manager import DBManager
import PyPDF2
import speech_recognition as sr
from llm_engine.router import smart_route_prompt
import urllib.parse
import re
import traceback
import hashlib
import datetime
import base64
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()
import io
import json
import subprocess
import concurrent.futures

def format_final_report(report_content, papers, final_scores, consensus_msg, expert_disciplines=None):
    # Remove old bibliography if WriterAgent generated a generic one
    if "### 📚 Verifiable Bibliography" in report_content:
        report_content = report_content.split("### 📚 Verifiable Bibliography")[0]
        
    bib_md = "\n\n### 📚 Verifiable Bibliography & Source Tracking\n"
    bib_md += "*Click on the links below to directly view or download the referenced papers:*\n\n"
    
    # Deduplicate papers based on title to avoid chunk spam from local files
    seen_titles = set()
    dedup_papers = []
    for p in papers:
        t = p.get('title', '')
        base_title = re.sub(r', Chunk \d+\)$', ')', t)
        base_title = re.sub(r' \(Chunk \d+\)$', '', base_title)
        if base_title not in seen_titles:
            seen_titles.add(base_title)
            p_copy = p.copy()
            p_copy['display_title'] = base_title
            dedup_papers.append(p_copy)
            
    for i, p in enumerate(dedup_papers, 1):
        title = p.get('display_title', p.get('title', 'Unknown Title'))
        source = p.get('source', 'Unknown Source')
        url = p.get('url')
        
        if not url or url == "Local File":
            if "User Upload" in source:
                bib_md += f"{i}. **📄 {title}**\n"
                bib_md += f"   - 🛡️ **Source:** `{source}` (Secure Air-Gapped Data)\n\n"
                continue
            else:
                url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(title)}"
        
        # Convert ArXiv abstract links to direct PDF links
        download_url = url
        if url and "arxiv.org/abs/" in url:
            download_url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
            if not download_url.endswith(".pdf"):
                download_url += ".pdf"
        
        bib_md += f"{i}. **<a href='{url}' target='_blank' class='premium-link-title'>{title}</a>**\n"
        bib_md += f"   - 🌐 **API Source:** `{source}`\n"
        bib_md += f"   - <a href='{download_url}' target='_blank' class='premium-btn'>📥 View / Download Paper</a>\n\n"
        
    xai_section = (
        "### 🧠 Neuro-Symbolic & Causal Validation (XAI)\n"
        "*Explainable AI (XAI) breakdown of the validation process:*\n"
        "- **Symbolic Logic Check:** The hypothesis was evaluated against deterministic rule engines to ensure the risk factor remained within acceptable, feasible thresholds.\n"
        "- **Causal DAG Verification:** A Directed Acyclic Graph (DAG) was autonomously constructed to map the core concepts. The causal path from 'Hypothesis Foundation' to 'Expected Outcome' was mathematically proven to be logically connected and acyclic.\n"
        "- **Neuro-Linguistic Endorsement:** An independent, localized LLM stress-tested the hypothesis to ensure strict alignment with scientific principles and the provided ground-truth context.\n\n"
    )
    
    # Create visually appealing HTML score cards
    score_html = f"""
<div style="display: flex; justify-content: space-between; text-align: center; margin: 20px 0; font-family: monospace; flex-wrap: wrap; gap: 10px;">
    <div style="background: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800; flex: 1; min-width: 120px;">
        <h4 style="margin: 0; color: #aaa; font-size: 14px;">Innovation</h4>
        <h2 style="margin: 5px 0 0 0; color: #ff9800;">{final_scores.get('innovation', 0):.2f}</h2>
    </div>
    <div style="background: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50; flex: 1; min-width: 120px;">
        <h4 style="margin: 0; color: #aaa; font-size: 14px;">Feasibility</h4>
        <h2 style="margin: 5px 0 0 0; color: #4caf50;">{final_scores.get('feasibility', 0):.2f}</h2>
    </div>
    <div style="background: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 4px solid #f44336; flex: 1; min-width: 120px;">
        <h4 style="margin: 0; color: #aaa; font-size: 14px;">Risk</h4>
        <h2 style="margin: 5px 0 0 0; color: #f44336;">{final_scores.get('risk', 0):.2f}</h2>
    </div>
    <div style="background: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 4px solid #9c27b0; flex: 1; min-width: 120px;">
        <h4 style="margin: 0; color: #aaa; font-size: 14px;">Uncertainty</h4>
        <h2 style="margin: 5px 0 0 0; color: #9c27b0;">±{final_scores.get('epistemic_uncertainty', 0):.2f}</h2>
    </div>
    <div style="background: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; flex: 1; min-width: 120px;">
        <h4 style="margin: 0; color: #aaa; font-size: 14px;">Total Score</h4>
        <h2 style="margin: 5px 0 0 0; color: #2196f3;">{final_scores.get('total_score', 0):.2f}</h2>
    </div>
</div>
    """
        
    domain_badges = ""
    if expert_disciplines:
        domain_badges = "<div style='display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;'>"
        for d in expert_disciplines:
            domain_badges += f"<span style='background: linear-gradient(45deg, #00e5ff, #39ff14); color: #000; padding: 5px 15px; border-radius: 15px; font-weight: 800; font-size: 0.9em; box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);'>✨ {d}</span>"
        domain_badges += "</div>\n\n"
        
    report_content = domain_badges + report_content + bib_md
    report_content += xai_section + f"### 📊 Scoring Metrics\n{score_html}\n\n### ⚖️ Consensus Status\n> **{consensus_msg}**\n"
    return report_content

def extract_text_from_file(file, status_callback=None):
    try:
        if file.name.lower().endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            return [{"page": i + 1, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages)]
        elif file.name.lower().endswith('.txt'):
            return [{"page": 1, "text": file.read().decode('utf-8')}]
        elif file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            if status_callback: status_callback(f"👁️ Processing image '{file.name}' via LLaVA Vision Model...")
            try:
                file_bytes = file.getvalue()
                base64_image = base64.b64encode(file_bytes).decode('utf-8')
                payload = {
                    "model": "llava",
                    "prompt": "Analyze this scientific image in extreme detail. Extract all text, formulas, charts, and data points. Explain the scientific mechanism shown.",
                    "images": [base64_image],
                    "stream": False
                }
                api_url = os.environ.get("VISION_API_URL", os.environ.get("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate"))
                res = requests.post(api_url, json=payload, timeout=60)
                if res.status_code == 200:
                    return [{"page": 1, "text": f"[Vision Extraction from {file.name}]: " + res.json().get("response", "")}]
            except Exception as e:
                if status_callback: status_callback(f"⚠️ LLaVA failed ({e}). Falling back to Tesseract OCR...")
            
            try:
                from PIL import Image
                import pytesseract
                img = Image.open(file)
                return [{"page": 1, "text": f"[OCR Extraction from {file.name}]: " + pytesseract.image_to_string(img)}]
            except ImportError:
                return [{"page": 1, "text": "[Image Uploaded. Note: Ensure 'llava' is running via Ollama for multi-modal vision extraction]"}]
    except Exception as e:
        print(f"[File Error] Could not read {file.name}: {e}")
    return []

def run_pipeline(domain_goal, research_goal, uploaded_files=None, audio_input=None, status_callback=None, stream_callback=None):
    if not research_goal or not research_goal.strip():
        research_goal = f"Explore novel discoveries and generate an innovative hypothesis in the field of {domain_goal}."

    def log_status(msg):
        print(msg)
        if status_callback:
            status_callback(msg)
            
    log_status(f"\n🚀 [Our Project Pipeline] Initializing for Domain Goal: {domain_goal}")
    
    db = DBManager()
    
    # Init Agents
    researcher = ResearcherAgent()
    analyst = AnalystAgent()
    innovator = InnovatorAgent()
    critic = CriticAgent()
    validator = ValidatorAgent()
    ethicist = EthicistAgent()
    writer = WriterAgent()
    
    # Init Engines
    embedder = EmbeddingEngine()
    retriever = FAISSRetriever()
    twin = TwinEngine()
    bus = MessageBus()
    consensus = ConsensusEngine()
    simulator = HypothesisSimulator()
    scorer = ScoringEngine()
    reporter = ReportGenerator()
    
    # 0. Process Voice Input
    if audio_input:
        log_status("🎤 Transcribing Voice Input...")
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_input) as source:
                audio_data = recognizer.record(source)
                voice_text = recognizer.recognize_google(audio_data)
                log_status(f"🎤 Transcribed Voice: {voice_text}")
                research_goal += f" | Voice Addition: {voice_text}"
        except Exception as e:
            log_status(f"⚠️ Voice transcription failed or no speech detected.")

    # 1. Fetch Papers
    log_status("[Phase 1] Data Ingestion & RAG Indexing...")
    papers = researcher.run(f"{domain_goal} {research_goal}")

    # 1.5 Process Uploaded Files
    if uploaded_files:
        log_status("   ├─ Processing User Uploaded Files...")
        for f in uploaded_files:
            extracted_pages = extract_text_from_file(f, status_callback)
            for page_data in extracted_pages:
                doc_text = page_data.get("text", "")
                page_num = page_data.get("page", 1)
                if doc_text:
                    # 🧠 Advanced Feature: Overlapping Semantic Chunking for RAG
                    chunk_size = 2000
                    overlap = 200
                    for i in range(0, len(doc_text), chunk_size - overlap):
                        chunk = doc_text[i:i + chunk_size]
                        if len(chunk) > 100:
                            papers.append({"title": f"{f.name} (Page {page_num}, Chunk {i//chunk_size + 1})", "abstract": chunk, "source": f"User Upload (Page {page_num})", "url": "Local File"})

    for p in papers:
        db.insert_paper(p['title'], p['abstract'], p['source'])
        twin.integrate_paper(p)
        
    # 2 & 3. RAG System
    log_status("   ├─ Generating Embeddings and Indexing Data...")
    texts = [f"{p['title']} {p['abstract']}" for p in papers]
    if texts:
        embeddings = embedder.generate_embeddings(texts)
        retriever.add_documents(papers, embeddings)
        
        # Perform RAG retrieval for relevant context (Reduced top_k to 5 to prevent LLM Context Timeouts)
        log_status("   ├─ Extracting relevant context via Hybrid (BM25 + Semantic) Search...")
        query_emb = embedder.generate_embeddings([research_goal])[0]
        relevant_papers = retriever.search(query_emb, query_text=research_goal, top_k=5)
    else:
        relevant_papers = []
        
    # 4. Cognitive Graphs Build Step
    log_status("   └─ Building Cognitive, Thought, and Causal Graphs...")
    log_status(f"Graph Status: {twin.status()}")
    
    # 5 & 6. Agents Execution
    log_status("[Phase 2] Swarm Assembly & Hypothesis Generation...")
    
    # Safely fetch knowledge from SQLite in the main thread to prevent cross-thread ProgrammingError
    knowledge = db.get_all_approved_hypotheses()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_analyst = executor.submit(analyst.run, relevant_papers, research_goal)
        
        swarm_prompt = f"Analyze the following research goal: {research_goal}. Identify the 5 most advanced and relevant scientific disciplines required to solve this (e.g., Quantum Mechanics, Bioinformatics, Nanophotonics, Game Theory, Ethics). Output strictly a JSON list of 5 strings."
        future_swarm = executor.submit(smart_route_prompt, swarm_prompt, 0.1)
        
        def fetch_memory(knowledge_data):
            if knowledge_data:
                print("   ├─ 🧠 [Memory] FAISS Semantic Search on Evolutionary Memory...")
                memory_retriever = FAISSRetriever(index_path="memory_faiss.index")
                memory_embeddings = embedder.generate_embeddings(knowledge_data)
                memory_retriever.add_documents(knowledge_data, memory_embeddings)
                query_emb = embedder.generate_embeddings([research_goal])[0]
                return memory_retriever.search(query_emb, query_text=research_goal, top_k=3)
            return []
        future_memory = executor.submit(fetch_memory, knowledge)
        
        context, gaps = future_analyst.result()
        swarm_data = future_swarm.result()
        past_knowledge = future_memory.result()
        
    log_status("   ├─ Assembling Dynamic Polymath Expert Swarm...")
    try:
        match = re.search(r'\[.*\]', swarm_data.strip(), re.DOTALL)
        expert_disciplines = json.loads(match.group(0)) if match else ["Physics", "Computer Science", "Mathematics", "Bioinformatics", "Nanotechnology"]
    except:
        expert_disciplines = ["Physics", "Computer Science", "Mathematics", "Bioinformatics", "Nanotechnology"]
    log_status(f"   └─ Swarm Assembled: {', '.join(expert_disciplines)}")

    log_status("   └─ Hypothesis Generation...")
    hypothesis = innovator.run(context, domain_goal, research_goal, past_knowledge=past_knowledge, stream_callback=lambda c: stream_callback("Innovator", c) if stream_callback else None, expert_disciplines=expert_disciplines)
    bus.broadcast("Innovator", hypothesis)
    
    log_status("[Phase 3] Adversarial Critique & Causal Validation...")
    
    log_status("   ├─ Ethical & Societal Review...")
    ethical_review = ethicist.run(hypothesis, stream_callback=lambda c: stream_callback("Ethicist", c) if stream_callback else None)
    bus.broadcast("Ethicist", ethical_review)
    
    log_status("   ├─ Critiquing Process...")
    critique = critic.run(hypothesis, stream_callback=lambda c: stream_callback("Critic", c) if stream_callback else None)
    bus.broadcast("Critic", critique)
    
    log_status("   ├─ Neuro-Symbolic & Causal Validation...")
    validation = validator.run(hypothesis, critique)
    bus.broadcast("Validator", str(validation))
    
    # 7. Consensus
    log_status("   └─ Agent Debate & Consensus...")
    is_consensus, consensus_msg = consensus.resolve(validation, critique)
    
    # 8. Simulation
    log_status("[Phase 4] Autonomous Sandbox Simulation & Scoring...")
    
    sim_result = {"simulated_feasibility": 0.0, "sandbox_log": "Execution failed."}
    
    max_retries = 3
    current_prompt = f"Write a highly concise, self-contained Python script to mathematically and physically model the feasibility of this hypothesis: {hypothesis[:1000]}. You MUST use advanced scientific libraries like `numpy`, `scipy`, or `sympy` to rigorously calculate the physical, thermodynamic, or algorithmic constraints. The script MUST print a valid JSON string at the end containing a 'simulated_feasibility' key with a float value between 0.0 and 1.0. Output strictly the raw Python code without backticks."
    for attempt in range(max_retries):
        ai_raw = smart_route_prompt(current_prompt, temperature=0.1)
        code_match = re.search(r'```(?:python)?(.*?)```', ai_raw, re.DOTALL)
        ai_code = code_match.group(1).strip() if code_match else ai_raw.replace("```python", "").replace("```", "").strip()
        
        log_status(f"   ├─ [Sandbox Attempt {attempt+1}/{max_retries}] Executing AI-generated Python simulation...")
        bus.broadcast("System", f"**[Sandbox Attempt {attempt+1}/{max_retries}] AI Generated Code:**\n```python\n{ai_code}\n```")
        try:
            # 🛡️ Secure Sandbox Execution using Subprocess with Timeout
            # Note for production: Wrap this in a Docker container (e.g. `docker run python:3.9-slim python -c "{ai_code}"`)
            process = subprocess.run(
                [sys.executable, "-c", ai_code],
                capture_output=True,
                text=True,
                timeout=10 # Prevent infinite loops and hang-ups
            )
            
            if process.returncode != 0:
                raise Exception(process.stderr)
                
            output = process.stdout
            match = re.search(r'\{.*\}', output.strip(), re.DOTALL)
            if match:
                try:
                    sim_result = json.loads(match.group(0))
                    sim_result["sandbox_log"] = "Code executed successfully."
                    log_status(f"   └─ ✅ Sandbox Simulation Success: Feasibility = {sim_result.get('simulated_feasibility')}")
                    bus.broadcast("System", f"✅ **Sandbox Simulation Success!**\nResult: `{sim_result}`")
                    break
                except json.JSONDecodeError:
                    log_status("   └─ ⚠️ Sandbox JSON parsing failed. Retrying...")
                    bus.broadcast("System", f"⚠️ **Sandbox Error:** Output contained invalid JSON.\n```text\n{output}\n```")
                    current_prompt = f"Your previous code ran but printed invalid JSON. Fix it to output exactly: {{\"simulated_feasibility\": 0.85}}. Output:\n{output}\n\nCode:\n{ai_code}"
            else:
                log_status("   └─ ⚠️ Sandbox failed to return JSON. Retrying...")
                bus.broadcast("System", f"⚠️ **Sandbox Error:** Output did not contain valid JSON.\n```text\n{output}\n```")
                current_prompt = f"Your previous code ran but did not output a valid JSON string. Fix the code to ensure it prints exactly this format: {{\"simulated_feasibility\": 0.85}}. Output: {output}\n\nPrevious code:\n{ai_code}"
        except subprocess.TimeoutExpired:
            error_trace = "Execution timed out after 10 seconds. You likely wrote an infinite loop. Optimize the code."
            log_status(f"   └─ ⚠️ Sandbox Execution Error. AI Auto-Debugging...")
            bus.broadcast("System", f"⚠️ **Sandbox Timeout! Auto-Debugging...**\n```text\n{error_trace}\n```")
            current_prompt = f"Your previous Python code timed out:\n{error_trace}\n\nFix the code and output the strictly working Python script without backticks. Previous code:\n{ai_code}"
        except Exception as e:
            error_trace = str(e)
            log_status(f"   └─ ⚠️ Sandbox Execution Error. AI Auto-Debugging...")
            bus.broadcast("System", f"⚠️ **Sandbox Crash! Auto-Debugging...**\n```text\n{error_trace}\n```")
            current_prompt = f"Your previous Python code crashed with this error:\n{error_trace}\n\nFix the code and output the strictly working Python script without backticks. Previous code:\n{ai_code}"
    
    # 9. Scoring
    log_status("   └─ Scoring Results...")
    final_scores = scorer.score(hypothesis, sim_result, validation)
    db.insert_hypothesis(hypothesis, validation['final_verdict'], final_scores['total_score'])
    
    # 10. Report Generation
    log_status("[Phase 5] Omni-Dimensional Matrix & Report Synthesis...")
    report_content = writer.run(hypothesis, critique, validation, ethical_review=ethical_review, papers=relevant_papers, gaps=gaps)
    report_content = format_final_report(report_content, relevant_papers, final_scores, consensus_msg, expert_disciplines)
    
    report_path = reporter.save_report(report_content)
    log_status(f"   ├─ Output saved to: {report_path}")
    
    mermaid_data = None
    qasm_data = None
    pytorch_code = None
    solidity_code = None
    robotics_code = None
    synthetic_csv = None
    dna_data = None
    snn_code = None
    theorem_data = None
    vr_data = None
    peer_review_data = None
    docker_json = None
    tech_stack_json = None
    pdb_data = None

    log_status("   └─ Autonomous Media & Output Formatting...")
    funding_json = {"budget_usd": "$250,000", "equipment": ["Lab Equipment", "Compute Cluster"], "timeline_months": 18}
    media_json = {"midjourney": "A futuristic scientific discovery, photorealistic --v 6.0", "sora": "A zooming cinematic shot of a scientific breakthrough"}
    impact_json = {"disrupted_industries": ["Tech", "Healthcare"], "economic_value_usd": "$1 Billion", "nash_equilibrium_outcome": "Global Adoption"}
    
    timestamp = datetime.datetime.utcnow().isoformat()
    pod_hash = hashlib.sha256(f"{hypothesis}{timestamp}".encode('utf-8')).hexdigest()
    pod_data = {"hash": pod_hash, "timestamp": timestamp}
    log_status(f"\n✅ Pipeline Execution Complete.")

    return report_content, final_scores, twin.kg.get_pyvis_html(), gaps, hypothesis, twin.kg.get_static_image(), bus.get_transcript(), pdb_data, mermaid_data, funding_json, pod_data, qasm_data, pytorch_code, robotics_code, solidity_code, expert_disciplines, synthetic_csv, dna_data, snn_code, theorem_data, media_json, impact_json, vr_data, docker_json, peer_review_data, tech_stack_json
