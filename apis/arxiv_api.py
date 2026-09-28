import requests
import xml.etree.ElementTree as ET
from functools import lru_cache
import urllib.parse

@lru_cache(maxsize=64)
def fetch_arxiv_papers(query: str, max_results: int = 5):
    safe_query = urllib.parse.quote(query)
    url = f"https://export.arxiv.org/api/query?search_query=all:{safe_query}&max_results={max_results}"
    try:
        headers = {"User-Agent": "AION-X-Discovery-Engine/2.0 (mailto:research@aionx.ai)"}
        response = requests.get(url, headers=headers, timeout=6.0)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        papers = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title")
            summary = entry.find("{http://www.w3.org/2005/Atom}summary")
            id_elem = entry.find("{http://www.w3.org/2005/Atom}id")
            
            paper_url = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
            for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
                if link.attrib.get("type") == "application/pdf":
                    paper_url = link.attrib.get("href", paper_url)
                    break
                elif link.attrib.get("rel") == "alternate":
                    paper_url = link.attrib.get("href", paper_url)
            
            if title is not None and summary is not None:
                clean_title = title.text.strip().replace("\n", " ")
                papers.append({
                    "title": clean_title,
                    "abstract": summary.text.strip().replace("\n", " "),
                    "source": "arXiv",
                    "url": paper_url or f"https://scholar.google.com/scholar?q={urllib.parse.quote(clean_title)}"
                })
        return papers
    except Exception as e:
        print(f"[arXiv API Warning]: {e}")
        return []
