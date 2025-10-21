# src/retriever.py
import chromadb
from sentence_transformers import SentenceTransformer
from src.config import STORAGE_DIR, TOP_K

class ChromaRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=f"{STORAGE_DIR}/chroma")
        self.collection = self.client.get_or_create_collection("fintech_projects")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve(self, query: str, k: int = TOP_K):
        emb = self.embedder.encode(query).tolist()
        results = self.collection.query(query_embeddings=[emb], n_results=k)
        docs = []
        for i in range(len(results["ids"][0])):
            docs.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "section_path": results["metadatas"][0][i].get("section", "ROOT"),
            })
        return docs
