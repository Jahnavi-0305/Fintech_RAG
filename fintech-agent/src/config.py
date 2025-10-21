import os
from dotenv import load_dotenv

load_dotenv()

# Base paths
DATA_PATH      = os.getenv("DATA_PATH", "data/Fintech_intake.docx")
STORAGE_DIR    = os.getenv("STORAGE_DIR", "storage")
CHUNKS_PATH    = f"{STORAGE_DIR}/chunks.jsonl"
BM25_PATH      = f"{STORAGE_DIR}/bm25_index.pkl"
CHROMA_PATH    = f"{STORAGE_DIR}/chroma"   # now defined AFTER STORAGE_DIR

# Model / API
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Retrieval params
TOP_K          = int(os.getenv("TOP_K", 12))
MAX_RERANKED   = int(os.getenv("MAX_RERANKED", 6))

# Generation params
TEMPERATURE    = float(os.getenv("TEMPERATURE", 0))
