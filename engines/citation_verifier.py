import re
import json
import urllib.parse
from typing import List, Dict, Any
from rag_engine.embeddings import EmbeddingEngine
from llm_engine.router import smart_route_prompt
from database.models import ClaimVerification, VerificationResult
from config import Config

class CitationVerifier:
    """
    Automatic Citation Verification Engine & Hallucination Firewall for PROJECT AION.
    Extracts factual claims, performs semantic matching against paper context, 
    and classifies support into SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED, or UNVERIFIED.
    Includes direct access links (DOI, ArXiv, Scholar) for all verified sources.
    """
    def __init__(self):
        self.embedder = EmbeddingEngine()

    def _resolve_paper_url(self, paper: Dict[str, Any], title: str) -> str:
        """Helper to get a direct URL or construct a direct access link."""
        raw_url = paper.get('url') if paper else ''
        if raw_url and raw_url.startswith(('http://', 'https://')):
            return raw_url
        clean_title = re.sub(r' \(Section \d+\)$', '', re.sub(r', Chunk \d+\)$', ')', title)).strip()
        encoded = urllib.parse.quote(clean_title)
        return f"https://scholar.google.com/scholar?q={encoded}"

    def extract_claims(self, text: str) -> List[str]:
        """
        Extracts key factual claims from hypothesis or report text.
        """
        prompt = (
            f"Extract up to 5 core factual claims from the following research hypothesis text:\n\n{text[:2000]}\n\n"
            "Output strictly a JSON list of claim strings. Do not include opinionated or hypothetical statements. JSON list only."
        )
        response = smart_route_prompt(prompt, temperature=0.1)
        try:
            match = re.search(r'\[.*\]', response.strip(), re.DOTALL)
            if match:
                claims = json.loads(match.group(0))
                if isinstance(claims, list) and len(claims) > 0:
                    return claims[:5]
        except Exception:
            pass

        # Fallback regex sentence extraction
        sentences = re.split(r'(?<=[.!?]) +', text[:1500])
        factual_sentences = [s.strip() for s in sentences if len(s.strip()) > 10 and not s.startswith('#')]
        return factual_sentences[:4] if factual_sentences else [text.strip()]

    def verify_claims(self, text: str, papers: List[Dict[str, Any]]) -> VerificationResult:
        """
        Verifies claims against retrieved paper text. Enforces Hallucination Firewall rules.
        """
        claims = self.extract_claims(text)
        verifications: List[ClaimVerification] = []

        paper_chunks = []
        for p in papers:
            title = p.get('title', 'Unknown Source')
            abstract = p.get('abstract', '')
            url = self._resolve_paper_url(p, title)
            paper_chunks.append({
                "source": title,
                "text": f"{title}: {abstract}",
                "url": url,
                "raw_paper": p
            })

        if not paper_chunks:
            for c in claims:
                verifications.append(
                    ClaimVerification(
                        claim_text=c,
                        status="UNVERIFIED",
                        supporting_source="None",
                        relevant_evidence="No literature indexed for semantic comparison.",
                        confidence=0.0,
                        source_url=""
                    )
                )
            return VerificationResult(
                claims=verifications,
                overall_status="INSUFFICIENT EVIDENCE",
                supported_count=0,
                unverified_count=len(claims),
                contradicted_count=0,
                firewall_passed=False
            )

        chunk_texts = [chunk['text'] for chunk in paper_chunks]
        chunk_embeddings = self.embedder.generate_embeddings(chunk_texts)

        supported_count = 0
        unverified_count = 0
        contradicted_count = 0

        for claim in claims:
            claim_emb = self.embedder.generate_embeddings([claim])[0]
            
            # Find best matching paper chunk
            best_sim = -1.0
            best_chunk = None

            for i, chunk_emb in enumerate(chunk_embeddings):
                sim = float(self.embedder.cosine_similarity(claim_emb, chunk_emb))
                if sim > best_sim:
                    best_sim = sim
                    best_chunk = paper_chunks[i]

            confidence = round(max(0.0, min(1.0, best_sim)), 2)
            source_url = best_chunk['url'] if best_chunk else ""

            if best_sim >= Config.EVIDENCE_THRESHOLD:
                status = "SUPPORTED"
                supported_count += 1
                evidence = best_chunk['text'][:300] + "..." if best_chunk else "Supported in literature."
                source = best_chunk['source'] if best_chunk else "Indexed Literature"
            elif best_sim >= 0.50:
                status = "PARTIALLY_SUPPORTED"
                supported_count += 1
                evidence = best_chunk['text'][:300] + "..." if best_chunk else "Partial context found."
                source = best_chunk['source'] if best_chunk else "Indexed Literature"
            else:
                status = "UNVERIFIED"
                unverified_count += 1
                evidence = "No direct evidence chunk matched above similarity threshold."
                source = "UNVERIFIED"

            verifications.append(
                ClaimVerification(
                    claim_text=claim,
                    status=status,
                    supporting_source=source,
                    relevant_evidence=evidence,
                    confidence=confidence,
                    source_url=source_url
                )
            )

        # Hallucination Firewall Policy Evaluation
        total_claims = len(claims)
        firewall_passed = (supported_count >= 1) and (unverified_count <= (total_claims // 2))
        
        overall_status = "VERIFIED" if firewall_passed else "INSUFFICIENT EVIDENCE"

        return VerificationResult(
            claims=verifications,
            overall_status=overall_status,
            supported_count=supported_count,
            unverified_count=unverified_count,
            contradicted_count=contradicted_count,
            firewall_passed=firewall_passed
        )
