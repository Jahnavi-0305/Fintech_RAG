## Internal Fintech Agent (LLM + RAG) — **Groq-only**

### Objective

Build a production-ready internal agent that **precisely** extracts information from `Fintech_intake.docx` using **Groq** LLM + a robust **RAG** pipeline (BM25 + LLM re-ranking), with **strict irrelevance exclusion** and **auditable citations**.

---

## 1) Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
touch .env.example

# set GROQ_API_KEY
save .env.example with these:
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DATA_PATH=data/Fintech_intake.docx
STORAGE_DIR=storage
TOP_K=12
MAX_RERANKED=6
TEMPERATURE=0

cp .env.example .env 
mkdir -p data storage
# Put your Fintech_intake.docx into ./data
python -m scripts.ingest
python -m scripts.index
```

### Run API

```bash
 python -m src.server
```
---

## 2) Conversation, not Q&A

* The API is stateless by default. For conversation flow, keep a **`history`** array on the client and pass a **dialogue-aware query** (e.g., resolve pronouns) to `/chat`. The agent prompt already handles elliptical questions (“What about status?”) as long as you include brief prior context in the `question` string.

---

## 3) Validation

```bash
python scripts/validate.py
# See ValidationReport.md for exact answers + chunk IDs
```
