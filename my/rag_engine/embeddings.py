from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    def __init__(self, model_name="paraphrase-albert-small-v2"):
        self.model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts, batch_size=64):
        if not texts:
            return []
        
        # Utilizing a larger batch_size to process multiple abstracts in parallel for higher throughput
        return self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
