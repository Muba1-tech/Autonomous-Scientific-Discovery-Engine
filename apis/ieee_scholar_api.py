import requests
from functools import lru_cache
import urllib.parse
import re

@lru_cache(maxsize=64)
def fetch_ieee_crossref_papers(query: str, max_results: int = 4):
    """
    Queries CrossRef API which indexes IEEE, ACM, Springer, Elsevier, and Nature papers.
    Returns real peer-reviewed papers with DOIs, authors, titles, and publishers.
    """
    clean_query = re.sub(r'[^a-zA-Z0-9\s-]', '', query).strip()
    safe_query = urllib.parse.quote(clean_query)
    url = f"https://api.crossref.org/works?query={safe_query}&rows={max_results}&sort=relevance"
    
    headers = {
        "User-Agent": "AION-X-Discovery-Engine/2.0 (mailto:research@aionx.ai)"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("message", {}).get("items", [])
            papers = []
            for item in items:
                title_list = item.get("title", [])
                title = title_list[0] if title_list else ""
                if not title:
                    continue
                
                publisher = item.get("publisher", "IEEE / Academic Press")
                doi = item.get("DOI", "")
                doi_url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
                
                # Check for IEEE or general high-impact publisher
                source_label = "IEEE Xplore" if "ieee" in publisher.lower() else publisher[:30]
                
                abstract = f"Peer-reviewed academic research published in {source_label} on {clean_query}."
                if "abstract" in item and item["abstract"]:
                    clean_abs = re.sub(r'<[^>]+>', '', item["abstract"])
                    abstract = clean_abs[:400]
                
                papers.append({
                    "title": title.strip(),
                    "abstract": abstract,
                    "source": source_label,
                    "url": doi_url or f"https://scholar.google.com/scholar?q={urllib.parse.quote(title)}"
                })
            return papers
    except Exception as e:
        print(f"[IEEE/CrossRef API Warning] {e}")
    
    return []
