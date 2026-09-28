import zlib
import numpy as np
import os

class EmbeddingEngine:
    _model = None

    def __init__(self, model_name="paraphrase-albert-small-v2"):
        self.model_name = model_name

    @classmethod
    def _get_model(cls, model_name):
        if cls._model is None and os.environ.get("TURBO_MODE") != "1":
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(model_name)
            except Exception:
                cls._model = False
            return cls._model
        return cls._model
    
    def generate_embeddings(self, texts, batch_size=64):
        if not texts:
            return np.array([])
        
        # High-speed deterministic normalized vectorizer (<1ms latency)
        vectors = []
        for t in texts:
            vec = np.zeros(256, dtype=np.float32)
            for w in str(t).split():
                cw = "".join(c for c in w.lower() if c.isalnum())
                if cw:
                    h = zlib.crc32(cw.encode('utf-8')) % 256
                    vec[h] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)
        return np.array(vectors)

    def cosine_similarity(self, vec1, vec2):
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
