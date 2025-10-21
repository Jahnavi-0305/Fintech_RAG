import orjson as json, pickle, os, regex as re
from rank_bm25 import BM25Okapi
from src.config import CHUNKS_PATH, BM25_PATH, STORAGE_DIR

_tok = lambda t: re.findall(r"\p{L}+|\p{N}+", (t or "").lower())

if __name__ == "__main__":
    os.makedirs(STORAGE_DIR, exist_ok=True)
    chunks = [json.loads(line) for line in open(CHUNKS_PATH, "rb").read().splitlines()]
    tokenized = [_tok(c["text"]) for c in chunks]
    bm25 = BM25Okapi(tokenized)
    with open(BM25_PATH, "wb") as f:
        pickle.dump((bm25, tokenized), f)
    print(f"Saved BM25 → {BM25_PATH} ({len(chunks)} chunks)")
