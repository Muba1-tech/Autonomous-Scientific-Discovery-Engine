"""
AION LLaMA3 Handler — Optimized wrapper that now routes through the fast router.
All direct Ollama calls now go through fast_ollama_call (25s timeout, instant cloud fallback).
Backwards-compatible: all existing agents calling generate_text() continue to work.
"""

import re
import time
import os
import json
from llm_engine.router import smart_route_prompt, fallback_cloud_call

_llm_cache = {}

def generate_text(
    prompt: str,
    system_prompt: str = None,
    json_mode: bool = False,
    temperature: float = 0.3,
    top_p: float = 0.9,
    max_retries: int = 1,           # Reduced to 1 — router handles fallback automatically
    stream_callback=None
) -> str:
    """
    Backwards-compatible text generation entry point.
    Now routes through smart_route_prompt for optimal speed + reliability.
    """
    # Compose full prompt including system context
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

    # Route through smart router (handles TURBO_MODE, caching, Ollama → Gemini fallback)
    response = smart_route_prompt(full_prompt, temperature=temperature, top_p=top_p)

    # Stream simulation if callback provided
    if stream_callback and response:
        for word in response.split(" "):
            stream_callback(word + " ")
            time.sleep(0.005)

    if response:
        _llm_cache[cache_key] = response

    return response or "[Generation unavailable — local and cloud LLMs both failed.]"
