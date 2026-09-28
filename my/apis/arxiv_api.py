import requests
import xml.etree.ElementTree as ET
from functools import lru_cache
import urllib.parse

@lru_cache(maxsize=32)
def fetch_arxiv_papers(query: str, max_results: int = 5):
    safe_query = urllib.parse.quote(query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{safe_query}&max_results={max_results}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        papers = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text
            papers.append({"title": title.strip(), "abstract": summary.strip(), "source": "arXiv"})
        return papers
    except Exception as e:
        print(f"[arXiv API Error]: {e}")
        return []
