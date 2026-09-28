import faiss
import numpy as np
import os
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

class FAISSRetriever:
    def __init__(self, dim=768, index_path="local_faiss.index"):
        self.dim = dim
        self.index_path = index_path
        self.index = faiss.IndexFlatL2(dim)
        self.documents = []
        self.bm25 = None
    
    def add_documents(self, docs, embeddings):
        if not docs or len(embeddings) == 0:
            return
        embeddings_np = np.array(embeddings).astype('float32')
        
        try:
            self.index.add(embeddings_np)
        except Exception as e:
            print(f"⚠️ [FAISS Error] Dimension mismatch or corruption detected ({e}). Rebuilding index...")
            # Automated Recovery: Auto-correct dimensionality and clear corrupted memory
            self.dim = embeddings_np.shape[1]
            self.index = faiss.IndexFlatL2(self.dim)
            self.documents = []
            self.index.add(embeddings_np)
            
        self.documents.extend(docs)
        
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception as e:
            print(f"⚠️ [FAISS Error] Failed to save index ({e}). Clearing corrupted file...")
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
                
        # Initialize BM25 Sparse Index with tokenized documents
        if BM25Okapi:
            tokenized_corpus = []
            for doc in self.documents:
                text = doc.get('abstract', '') if isinstance(doc, dict) else str(doc)
                tokenized_corpus.append(text.lower().split())
            self.bm25 = BM25Okapi(tokenized_corpus)
    
    def search(self, query_embedding, query_text="", top_k=3, alpha=0.5):
        if self.index.ntotal == 0:
            return []
            
        query_np = np.array([query_embedding]).astype('float32')
        
        if not self.bm25 or not query_text:
            # Fallback to standard FAISS if BM25 is not available or no query text is provided
            distances, indices = self.index.search(query_np, top_k)
            results = []
            for idx in indices[0]:
                if 0 <= idx < len(self.documents):
                    results.append(self.documents[idx])
            return results

        # Hybrid Search: Fetch a wider pool (top_k * 5) from FAISS for re-ranking
        fetch_k = min(top_k * 5, len(self.documents))
        distances, indices = self.index.search(query_np, fetch_k)
        
        # 1. Calculate Dense Scores (Normalized FAISS L2 Distances)
        dense_scores = {}
        max_dist = max(distances[0]) if len(distances[0]) > 0 and max(distances[0]) > 0 else 1.0
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.documents):
                dense_scores[idx] = 1.0 - (distances[0][i] / max_dist)
                
        # 2. Calculate Sparse Scores (BM25)
        tokenized_query = query_text.lower().split()
        doc_scores = self.bm25.get_scores(tokenized_query)
        max_bm25 = max(doc_scores) if max(doc_scores) > 0 else 1.0
        
        # 3. Hybrid Reciprocal Rank Fusion
        hybrid_scores = []
        for idx in dense_scores.keys():
            bm25_score = doc_scores[idx] / max_bm25
            hybrid_score = (alpha * dense_scores[idx]) + ((1 - alpha) * bm25_score)
            hybrid_scores.append((hybrid_score, idx))
            
        # Sort by best combined hybrid score
        hybrid_scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for _, idx in hybrid_scores[:top_k]:
            results.append(self.documents[idx])
            
        return results
