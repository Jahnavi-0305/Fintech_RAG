import sys, json as pyjson
from src.retriever import BM25Retriever
from src.agent import rerank_chunks, answer
from src.config import BM25_PATH, CHUNKS_PATH, TOP_K

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Team Members for Data Masking Tool — return only names"
    retriever = BM25Retriever.load(BM25_PATH, CHUNKS_PATH)
    retrieved = retriever.retrieve(q, TOP_K)
    selected = rerank_chunks(q, retrieved)
    res = answer(q, selected)
    print("\n=== ANSWER ===")
    if isinstance(res["answer"], dict):
        print(pyjson.dumps(res["answer"], indent=2, ensure_ascii=False))
    else:
        print(res["answer"])
    print("\nUsed Chunks:", res["used_chunks"])
