import requests
import time
import random
import json
import os
import re
from llm_engine.router import fallback_cloud_call

_llm_cache = {}

def generate_text(prompt: str, system_prompt: str = None, json_mode: bool = False, temperature: float = 0.1, top_p: float = 0.9, max_retries: int = 3, stream_callback=None) -> str:
    if os.environ.get("TURBO_MODE") == "1":
        # Extract the target domain dynamically if it exists in the prompt
        domain_match = re.search(r'Target Domain:\s*(.*?)\n', prompt)
        domain = domain_match.group(1).strip() if domain_match else "Advanced Sciences"
        
        mock_text = f"**[🚀 TURBO DEMO MODE]**\n\n### 📐 First Principles Derivation\nCore mathematical axioms verified instantly for **{domain}**. The system's total energy state can be modeled via the Hamiltonian:\n\n$$ \\hat{{H}} = \\sum_{{i=1}}^{{N}} \\frac{{\\hat{{p}}_i^2}}{{2m}} + V(\\hat{{r}}_1, \\dots, \\hat{{r}}_N) $$\n\n### 🎯 Direct Answer\nThis is a highly optimized and accelerated simulated response for demonstration in the field of {domain}.\n\n### 🚀 Novel Hypothesis\nBy synthesizing advanced cross-domain architectures, we achieve a massive leap in theoretical feasibility regarding {domain}.\n\n### 🧠 Detailed Reasoning & Synthesis\n- Domain 1 Perspective: Thermodynamics validate the bounds of {domain}.\n- Domain 2 Perspective: The algorithmic complexity is vastly reduced.\n- Domain 3 Perspective: The topology maps perfectly to the required structure.\n- Domain 4 Perspective: The biological integration is sound.\n- Domain 5 Perspective: The nanomaterials provide adequate tensile strength."
        if stream_callback:
            for chunk in mock_text.split(" "):
                stream_callback(chunk + " ")
                time.sleep(0.02)
        return mock_text

    if os.environ.get("FORCE_GEMINI") == "1":
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        response = fallback_cloud_call(full_prompt, "gemini", temperature)
        if stream_callback:
            for chunk in response.split(" "):
                stream_callback(chunk + " ")
                time.sleep(0.01)
        return response

    cache_key = f"{prompt}_temp{temperature}_top{top_p}"
    # Only return cached output if it was previously successful
    if cache_key in _llm_cache:
        if stream_callback:
            stream_callback(_llm_cache[cache_key])
        return _llm_cache[cache_key]
        
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": stream_callback is not None,
        "keep_alive": "1h",  # 🚀 Advanced: Keeps model in VRAM for lightning-fast multi-agent debate
        "options": {
            "num_ctx": 4096,     # Restrict context window to save memory bandwidth
            "num_predict": 1024, # Cap output tokens to prevent rambling
            "num_thread": 8,     # Maximize physical CPU core usage
            "temperature": temperature,
            "top_p": top_p
        }
    }
    
    if system_prompt:
        payload["system"] = system_prompt
    if json_mode:
        payload["format"] = "json"  # 🚀 Advanced: Forces deterministic structured data extraction
        
    for attempt in range(max_retries):
        try:
            api_url = os.environ.get("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
            response = requests.post(
                api_url,
                json=payload,
                timeout=180,  # Reduced timeout to trigger retries quicker
                stream=stream_callback is not None
            )
            if response.status_code == 200:
                if stream_callback:
                    output = ""
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line.decode('utf-8')).get("response", "")
                            output += chunk
                            stream_callback(chunk)
                    _llm_cache[cache_key] = output.strip()
                    return output.strip()
                else:
                    output = response.json().get("response", "").strip()
                    _llm_cache[cache_key] = output  # Save successful generation to memory
                    return output
            else:
                print(f"⚠️ [LLaMA3 Warning]: API status {response.status_code}. Retrying ({attempt + 1}/{max_retries})...")
        except requests.exceptions.Timeout:
            print(f"⏳ [LLaMA3 Timeout]: Attempt {attempt + 1}/{max_retries} timed out. Retrying...")
        except Exception as e:
            return f"[Fallback Error]: Details: {str(e)}"
            
        # 🚀 Advanced: Exponential backoff with jitter to gracefully handle GPU spikes
        backoff_time = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(backoff_time)

    return "[LLM Generation Failed]: The local model timed out or encountered an error after multiple retries."
