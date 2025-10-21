# Internal Fintech Agent (LLM + RAG) — Groq-only

**Objective:** Precisely extract answers from `Fintech_intake.docx` with strict irrelevance exclusion, dynamic retrieval, conversation flow, and auditable citations.

## 1) Setup

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # paste your GROQ_API_KEY
mkdir -p data storage
# Put Fintech_intake.docx into ./data
python -m scripts.ingest
python -m scripts.index
