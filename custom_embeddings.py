from sentence_transformers import SentenceTransformer
from typing import List, Optional

class CustomHuggingFaceEmbeddings:
    """A simpler wrapper for HuggingFace embeddings that avoids the pickle issue."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the embedding model."""
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query."""
        embedding = self.model.encode([text])[0]
        return embedding.tolist()