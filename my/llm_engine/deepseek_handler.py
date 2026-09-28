import requests
import time
import random
import json
import os
from llm_engine.router import fallback_cloud_call

_llm_cache = {}

def analyze_text(prompt: str, system_prompt: str = None, json_mode: bool = False, temperature: float = 0.1, top_p: float = 0.9, max_retries: int = 3, stream_callback=None) -> str:
    if os.environ.get("TURBO_MODE") == "1":
        if "FORMAT REQUIREMENT" in prompt and "table" in prompt:
            mock_text = "| Pros (Strengths) | Cons (Flaws/Risks) |\n|---|---|\n| Exponential efficiency gains | Theoretical stability limits |\n| Radical architectural innovation | High resource cost for physical validation |"
        else:
            mock_text = "**[🚀 TURBO DEMO MODE]** Validated successfully. The causal chain is logically sound and mathematically provable."
        
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
    if cache_key in _llm_cache:
        if stream_callback:
            stream_callback(_llm_cache[cache_key])
        return _llm_cache[cache_key]
        
    payload = {
        "model": "deepseek-coder:6.7b",
        "prompt": prompt,
        "stream": stream_callback is not None,
        "keep_alive": "1h",  # 🚀 Advanced: Keeps model loaded in VRAM
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
        payload["format"] = "json"
        
    for attempt in range(max_retries):
        try:
            api_url = os.environ.get("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
            response = requests.post(
                api_url,
                json=payload,
                timeout=180,
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
                    _llm_cache[cache_key] = output
                    return output
            else:
                print(f"⚠️ [DeepSeek Warning]: API status {response.status_code}. Retrying ({attempt + 1}/{max_retries})...")
        except requests.exceptions.Timeout:
            print(f"⏳ [DeepSeek Timeout]: Attempt {attempt + 1}/{max_retries} timed out. Retrying...")
        except Exception as e:
            return f"[Fallback Error]: Details: {str(e)}"
            
        # 🚀 Advanced: Exponential backoff with jitter
        backoff_time = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(backoff_time)

    return "[LLM Generation Failed]: The local model timed out or encountered an error after multiple retries."
