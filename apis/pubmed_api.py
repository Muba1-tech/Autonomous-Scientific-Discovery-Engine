import requests
from functools import lru_cache
import urllib.parse
import re

@lru_cache(maxsize=64)
def fetch_pubmed_papers(query: str, max_results: int = 4):
    clean_query = re.sub(r'[^a-zA-Z0-9\s-]', '', query).strip()
    safe_query = urllib.parse.quote(clean_query)
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={safe_query}&retmode=json&retmax={max_results}"
    try:
        search_resp = requests.get(search_url, timeout=3).json()
        ids = search_resp.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(ids)}&retmode=json"
        summary_resp = requests.get(summary_url, timeout=3).json()
        
        papers = []
        for uid in ids:
            doc = summary_resp.get("result", {}).get(uid, {})
            title = doc.get("title", "")
            if title:
                papers.append({
                    "title": title.strip(),
                    "abstract": f"Peer-reviewed medical/biomedical publication regarding {clean_query}.",
                    "source": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                })
        return papers
    except Exception:
        return []
