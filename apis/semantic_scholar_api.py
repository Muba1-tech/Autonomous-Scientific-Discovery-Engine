import requests
from functools import lru_cache
import urllib.parse

@lru_cache(maxsize=64)
def fetch_semantic_scholar_papers(query: str, limit: int = 5):
    safe_query = urllib.parse.quote(query)
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={safe_query}&limit={limit}&fields=title,abstract"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code != 200:
            return []
        data = response.json()
        papers = []
        for item in data.get("data", []):
            if item.get("abstract"):
                paper_id = item.get("paperId", "")
                url = item.get("url") or (item.get("openAccessPdf", {}) or {}).get("url")
                if not url and paper_id:
                    url = f"https://www.semanticscholar.org/paper/{paper_id}"
                clean_title = item.get("title", "").strip()
                papers.append({
                    "title": clean_title,
                    "abstract": item.get("abstract", "").strip(),
                    "source": "Semantic Scholar",
                    "url": url or f"https://scholar.google.com/scholar?q={urllib.parse.quote(clean_title)}"
                })
        return papers
    except Exception:
        return []
