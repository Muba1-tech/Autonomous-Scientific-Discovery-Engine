import re
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
import time
import random

_router_cache = {}

def fallback_cloud_call(prompt: str, model: str, temperature: float) -> str:
    """Uses Google Gemini's lifetime free developer tier as a fallback if the local Ollama instance crashes."""
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyC1lpl4L8-OFDfo1le7lEqFXRL5yhsfu_o")
    if not api_key:
        return "[Fallback]: Local LLM failed and no GEMINI_API_KEY provided in .env for cloud fallback."
        
    print(f"☁️ [Cloud Fallback] Routing request to Google Gemini API (Free Tier)...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature}
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[Fallback]: Both Local and Cloud LLMs failed. Details: {e}"

def fast_ollama_call(prompt: str, model: str, temperature: float, top_p: float, max_retries: int = 3) -> str:
    """Highly optimized local Ollama API call for <3s latency."""
    url = os.environ.get("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "1h", # 🚀 Keep model loaded in VRAM (Massive speedup)
        "options": {
            "num_ctx": 4096,     # Restrict context window to save memory bandwidth
            "num_predict": 1024, # Cap output tokens to prevent rambling
            "num_thread": 8,     # Maximize physical CPU core usage
            "temperature": temperature,
            "top_p": top_p
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            print(f"⏳ [Ollama Timeout] Attempt {attempt + 1}/{max_retries} timed out. Retrying...")
        except Exception as e:
            print(f"⚠️ [Ollama API Error] Failed to contact {model} on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return f"[Fallback]: Generated hypothesis placeholder due to local LLM unavailability. Details: {e}"
                
        # Exponential backoff with jitter before retrying local Ollama
        backoff_time = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(backoff_time)
        
    # If local Ollama completely failed all retries, trigger the cloud fallback
    return fallback_cloud_call(prompt, model, temperature)

def calculate_cognitive_entropy(prompt: str) -> float:
    """Calculates the semantic 'entropy' (open-endedness) of the prompt to dynamically scale the temperature."""
    creative_words = ['brainstorm', 'novel', 'radical', 'imagine', 'synthesize', 'explore', 'innovate', 'propose', 'crossover']
    deterministic_words = ['calculate', 'prove', 'validate', 'evaluate', 'summarize', 'extract', 'format', 'flaws']
    
    c_score = sum(1 for w in creative_words if w in prompt.lower())
    d_score = sum(1 for w in deterministic_words if w in prompt.lower())
    
    # Base temp is 0.3. High creativity raises it, deterministic logic lowers it.
    temp = 0.3 + (c_score * 0.15) - (d_score * 0.15)
    return max(0.01, min(0.95, temp))

def smart_route_prompt(prompt: str, temperature: float = None, top_p: float = 0.9) -> str:
    """
    Dynamically routes the prompt to the most capable model based on cognitive requirements.
    """
    if os.environ.get("TURBO_MODE") == "1":
        time.sleep(0.1)
        if "Python script to mathematically model" in prompt or "simulated_feasibility" in prompt:
            return "print('{\"simulated_feasibility\": 0.92}')"
        if "JSON" in prompt or "{" in prompt:
            if "innovation" in prompt: return '{"innovation": 0.95, "risk": 0.05}'
            if "budget_usd" in prompt: return '{"budget_usd": "$250,000", "equipment": ["Quantum Simulator", "Graphene Substrates"], "timeline_months": 18}'
            if "midjourney" in prompt: return '{"midjourney": "A futuristic glowing quantum biolab, photorealistic --v 6.0", "sora": "Zooming into a glowing molecule"}'
            if "disrupted_industries" in prompt: return '{"disrupted_industries": ["Healthcare", "Energy"], "economic_value_usd": "$5 Trillion", "nash_equilibrium_outcome": "Global cooperative adoption"}'
            if "dockerfile" in prompt: return '{"dockerfile": "FROM python:3.10\\nRUN pip install torch", "docker_compose": "version: \\"3.9\\""}'
            if "project_name" in prompt: return '{"project_name": "Neuro-Quantum Control Interface", "tech_stack": ["React", "FastAPI", "snnTorch"], "architecture_description": "A microservices architecture.", "mermaid_data": "graph TD\\n A-->B", "qasm_data": "OPENQASM 2.0;", "pytorch_code": "import torch", "solidity_code": "pragma solidity ^0.8.0;", "robotics_code": "from opentrons import protocol_api", "synthetic_csv": "time,val\\n0,0", "dna_data": ">DNA\\nATCG", "snn_code": "import snntorch", "theorem_data": "E=mc^2", "vr_data": "<a-scene></a-scene>", "dockerfile": "FROM python", "docker_compose": "version: 3", "peer_review_data": "Critique.", "pdb_data": "HEADER EMPTY"}'
            return '["Quantum Physics", "Synthetic Biology", "Advanced Mathematics", "Bioinformatics", "Nanotechnology"]'
        if "Mermaid.js flowchart" in prompt: return "graph TD\n    A[Start] --> B[Simulate]\n    B --> C[Validate]"
        if "OpenQASM" in prompt: return "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];"
        if "snnTorch" in prompt or "PyTorch" in prompt or "Opentrons" in prompt: return "import torch\nimport snntorch as snn\n# Mocked AI code\nprint('Executing AI simulation...')"
        if "Solidity" in prompt: return "pragma solidity ^0.8.0;\ncontract DiscoveryIP {\n    string public ipHash = \"mock_hash\";\n}"
        if "dataset" in prompt or "CSV" in prompt: return "time_ms,control_group,experimental_group,causal_effect\n0,1.0,1.0,0.0\n10,1.0,1.5,0.5\n20,0.9,2.1,1.2"
        if "synthetic DNA" in prompt or "FASTA" in prompt: return ">HYPOTHESIS_DNA\nATCGGCTAGCTAGCATCG"
        return "**[🚀 TURBO DEMO MODE]** Fast deterministic text response."

    if temperature is None:
        temperature = calculate_cognitive_entropy(prompt)
        print(f"🌡️ [LLM Router] Dynamic Cognitive Entropy calculated: Temp set to {temperature:.2f}")

    cache_key = f"{prompt}_temp{temperature}_top{top_p}"
    if cache_key in _router_cache:
        print("⚡ [LLM Router] Cache hit -> Returning saved response")
        return _router_cache[cache_key]
        
    # Keywords indicating a need for math, logic, coding, or rigorous causal inference
    logic_math_keywords = [
        r'\bmath(ematics)?\b', r'\blogic(al)?\b', r'\bcalculate\b', r'\bequation\b',
        r'\bformula\b', r'\balgorithm(ic)?\b', r'\bproof\b', r'\bcausal(ity)?\b',
        r'\bstatistics\b', r'\bcode\b', r'\bpython\b', r'\bvalidate\b', r'\btheorem\b'
    ]
    
    is_logic_task = any(re.search(kw, prompt.lower()) for kw in logic_math_keywords)
    
    if os.environ.get("FORCE_GEMINI") == "1":
        print("☁️ [LLM Router] Force Gemini API enabled -> Routing to Gemini")
        response = fallback_cloud_call(prompt, "gemini", temperature)
        _router_cache[cache_key] = response
        return response

    if is_logic_task:
        print("🧠 [LLM Router] Logic/Math detected -> Routing to DeepSeek-Coder (Optimized)")
        # DeepSeek handles the math and logic via high-speed API
        response = fast_ollama_call(prompt, "deepseek-coder:6.7b", temperature, top_p)
    else:
        print("✍️ [LLM Router] Creative/Writing detected -> Routing to LLaMA3 (Optimized)")
        # LLaMA3 handles writing and synthesis via high-speed API
        response = fast_ollama_call(prompt, "llama3", temperature, top_p)
        
    _router_cache[cache_key] = response
    return response