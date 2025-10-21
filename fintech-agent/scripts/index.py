# -*- coding: utf-8 -*-
import os, orjson as json, chromadb
from sentence_transformers import SentenceTransformer
from src.config import CHUNKS_PATH, STORAGE_DIR

if __name__ == "__main__":
    os.makedirs(os.path.join(STORAGE_DIR, "chroma"), exist_ok=True)
    client = chromadb.PersistentClient(path=os.path.join(STORAGE_DIR, "chroma"))
    collection = client.get_or_create_collection("fintech_projects")

    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # Read chunks
    chunks = [json.loads(line) for line in open(CHUNKS_PATH, "rb").read().splitlines()]

    # Safely clear existing records
    try:
        existing = collection.get()
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception as e:
        print(f"⚠️ Skipped clearing existing docs: {e}")

    print(f"Indexing {len(chunks)} chunks...")

    # Add chunks with embeddings
    for c in chunks:
        emb = embedder.encode(c["text"]).tolist()
        collection.add(
            ids=[c["id"]],
            embeddings=[emb],
            documents=[c["text"]],
            metadatas=[{"section": c["section_path"]}],
        )

    print("✅ ChromaDB index built at storage/chroma/")
