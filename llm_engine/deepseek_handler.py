"""
AION DeepSeek Handler — Optimized wrapper that routes through the fast router.
All direct Ollama calls now go through smart_route_prompt (25s timeout, instant cloud fallback).
Backwards-compatible: all existing agents calling analyze_text() continue to work.
"""

import re
import time
import os
from llm_engine.router import smart_route_prompt, fallback_cloud_call

_llm_cache = {}

def analyze_text(
    prompt: str,
    system_prompt: str = None,
    json_mode: bool = False,
    temperature: float = 0.1,
    top_p: float = 0.9,
    max_retries: int = 1,          # Router handles retries internally
    stream_callback=None
) -> str:
    """
    Backwards-compatible DeepSeek/analytics entry point.
    Now routes through smart_route_prompt for 25s timeout + instant cloud fallback.
    """
    full_prompt = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt

    if json_mode:
        full_prompt += "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no commentary."

    # Cache check
    cache_key = f"{full_prompt[:400]}|t={temperature:.2f}|p={top_p:.2f}"
    if cache_key in _llm_cache:
        result = _llm_cache[cache_key]
        if stream_callback:
            stream_callback(result)
        return result

    # Route through the smart router
    response = smart_route_prompt(full_prompt, temperature=temperature, top_p=top_p)

    if stream_callback and response:
        for word in response.split(" "):
            stream_callback(word + " ")
            time.sleep(0.005)

    if response:
        _llm_cache[cache_key] = response

    return response or "[Analysis unavailable — local and cloud LLMs both failed.]"
