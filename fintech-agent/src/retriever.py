import orjson as json
from rank_bm25 import BM25Okapi
import regex as re
from typing import List, Dict
import pickle

def _tok(t: str):
    return re.findall(r"\p{L}+|\p{N}+", (t or "").lower())

class ChunkStore:
    def __init__(self, chunks: List[Dict]):
        self.chunks = chunks
        self._by_id = {c["id"]: c for c in chunks}

    def get(self, cid: str) -> Dict:
        return self._by_id[cid]

class BM25Retriever:
    def __init__(self, bm25, tokenized_docs, store: ChunkStore):
        self.bm25 = bm25
        self.tokenized_docs = tokenized_docs
        self.store = store

    @classmethod
    def load(cls, bm25_path: str, chunks_path: str):
        with open(bm25_path, "rb") as f:
            bm25, tokenized_docs = pickle.load(f)
        chunks = [json.loads(line) for line in open(chunks_path, "rb").read().splitlines()]
        store = ChunkStore(chunks)
        return cls(bm25, tokenized_docs, store)

    def retrieve(self, query: str, k: int) -> List[Dict]:
        toks = _tok(query)
        scores = self.bm25.get_scores(toks)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self.store.chunks[i] for i in top_idx]
