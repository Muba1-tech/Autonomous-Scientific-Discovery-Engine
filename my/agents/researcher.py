from apis.arxiv_api import fetch_arxiv_papers
from apis.semantic_scholar_api import fetch_semantic_scholar_papers
from apis.pubmed_api import fetch_pubmed_papers
import concurrent.futures
import os
import re
import json

CACHE_FILE = "paper_cache.json"
MAX_CACHE_QUERIES = 50  # Prune the cache if it exceeds this many searches

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache_data):
    try:
        # Automatically remove oldest cached searches if it gets too large
        if len(cache_data) > MAX_CACHE_QUERIES:
            keys_to_remove = list(cache_data.keys())[:-MAX_CACHE_QUERIES]
            for k in keys_to_remove:
                del cache_data[k]
                
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Cache Error] Failed to save paper cache: {e}")

_paper_cache = load_cache()

class ResearcherAgent:
    def run(self, query):
        # Clean the query to prevent API crashes (remove special characters)
        clean_query = re.sub(r'[^a-zA-Z0-9\s-]', '', query).strip()
        # Truncate long paragraphs to the first ~12 words to act as a focused keyword search
        search_keywords = " ".join(clean_query.split()[:12])
        
        if search_keywords in _paper_cache:
            print(f"[Researcher] ⚡ Cache hit! Returning saved papers for: {search_keywords}")
            return _paper_cache[search_keywords]
            
        print(f"[Researcher] Fetching papers concurrently for: {search_keywords}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_arxiv = executor.submit(fetch_arxiv_papers, search_keywords, 10)
            future_ss = executor.submit(fetch_semantic_scholar_papers, search_keywords, 10)
            future_pubmed = executor.submit(fetch_pubmed_papers, search_keywords, 3)
            
            arxiv = future_arxiv.result()
            ss = future_ss.result()
            pubmed = future_pubmed.result()
            
        results = arxiv + ss + pubmed
        _paper_cache[search_keywords] = results
        save_cache(_paper_cache)
        return results
