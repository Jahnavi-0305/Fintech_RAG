## Internal Fintech Agent (LLM + RAG) — **Groq-only**

### Objective

Build a production-ready internal agent that **precisely** extracts information from `Fintech_intake.docx` using **Groq** LLM + a robust **RAG** pipeline (BM25 + LLM re-ranking), with **strict irrelevance exclusion** and **auditable citations**.

---

## 1) Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set GROQ_API_KEY
mkdir -p data storage
# Put your Fintech_intake.docx into ./data
python scripts/ingest.py
python scripts/index.py
```

### Run API

```bash
export FLASK_APP=src/server.py
python -m flask run --host 0.0.0.0 --port 8000
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
