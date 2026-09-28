import requests
from functools import lru_cache
import urllib.parse

@lru_cache(maxsize=32)
def fetch_pubmed_papers(query: str, max_results: int = 5):
    safe_query = urllib.parse.quote(query)
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={safe_query}&retmode=json&retmax={max_results}"
    try:
        search_resp = requests.get(search_url, timeout=10).json()
        ids = search_resp.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(ids)}&retmode=json"
        summary_resp = requests.get(summary_url, timeout=10).json()
        
        papers = []
        for uid in ids:
            doc = summary_resp.get("result", {}).get(uid, {})
            title = doc.get("title", "")
            papers.append({"title": title, "abstract": "PubMed abstract available via detailed fetch.", "source": "PubMed"})
        return papers
    except Exception as e:
        print(f"[PubMed API Error]: {e}")
        return []
