import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DATA_PATH      = os.getenv("DATA_PATH", "data/Fintech_intake.docx")
STORAGE_DIR    = os.getenv("STORAGE_DIR", "storage")
CHUNKS_PATH    = f"{STORAGE_DIR}/chunks.jsonl"
BM25_PATH      = f"{STORAGE_DIR}/bm25_index.pkl"
TOP_K          = int(os.getenv("TOP_K", 12))
MAX_RERANKED   = int(os.getenv("MAX_RERANKED", 6))
TEMPERATURE    = float(os.getenv("TEMPERATURE", 0))
