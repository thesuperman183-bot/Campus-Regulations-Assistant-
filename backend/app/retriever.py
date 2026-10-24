from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import EMBED_MODEL_NAME, TOP_K

_embedder: Optional[SentenceTransformer] = None


def get_embedder() -> SentenceTransformer:
    """Lazy loader for SentenceTransformer to allow quick startup."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder


class VectorStore:
    """
    In-memory vector store matching the Colab RAG pipeline.
    Maintains chunk text, metadata (document name, page number), and normalized vectors.
    """

    def __init__(self):
        self.chunks: List[Dict] = []
        self.vectors: Optional[np.ndarray] = None

    def add_chunks(self, chunks: List[Dict]) -> int:
        """
        Encodes chunks and updates the vector store.
        Returns the number of new chunks added.
        """
        if not chunks:
            return 0

        embedder = get_embedder()
        texts = [c["text"] for c in chunks]
        new_vectors = embedder.encode(texts, normalize_embeddings=True)

        if self.vectors is None or len(self.chunks) == 0:
            self.vectors = np.array(new_vectors, dtype=np.float32)
            self.chunks = list(chunks)
        else:
            self.vectors = np.vstack([self.vectors, np.array(new_vectors, dtype=np.float32)])
            self.chunks.extend(chunks)

        return len(chunks)

    def retrieve(self, question: str, top_k: int = TOP_K) -> List[Dict]:
        """
        Finds the chunks whose meaning is closest to the question using dot product
        over normalized embeddings (cosine similarity).
        """
        if not self.chunks or self.vectors is None:
            return []

        embedder = get_embedder()
        question_vector = embedder.encode([question], normalize_embeddings=True)[0]
        similarities = self.vectors @ question_vector

        # Cap top_k to total available chunks
        k = min(top_k, len(self.chunks))
        best_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in best_indices:
            chunk_copy = dict(self.chunks[idx])
            chunk_copy["score"] = float(similarities[idx])
            results.append(chunk_copy)

        return results

    def clear(self):
        """Clears all indexed chunks and vectors."""
        self.chunks = []
        self.vectors = None

    def list_documents(self) -> List[str]:
        """Returns unique document names currently in the store."""
        seen = set()
        docs = []
        for c in self.chunks:
            doc = c.get("document", "Unknown")
            if doc not in seen:
                seen.add(doc)
                docs.append(doc)
        return docs

    def total_chunks(self) -> int:
        return len(self.chunks)


# Global in-memory instance for backend session
knowledge_base = VectorStore()
