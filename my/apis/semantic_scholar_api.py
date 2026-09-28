import requests
from functools import lru_cache
import urllib.parse

@lru_cache(maxsize=32)
def fetch_semantic_scholar_papers(query: str, limit: int = 5):
    safe_query = urllib.parse.quote(query)
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={safe_query}&limit={limit}&fields=title,abstract"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        papers = []
        for item in data.get("data", []):
            if item.get("abstract"):
                papers.append({"title": item["title"], "abstract": item["abstract"], "source": "SemanticScholar"})
        return papers
    except Exception as e:
        print(f"[Semantic Scholar API Error]: {e}")
        return []
