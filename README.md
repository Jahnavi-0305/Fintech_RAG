

# Internal Fintech Agent (LLM + RAG with ChromaDB)

### **Objective**

Build a **production-ready internal agent** that precisely extracts information from `Fintech_intake.docx` using
**Groq LLM (Llama-3.3-70B)** + **ChromaDB vector retrieval**, delivering **plain-text, context-grounded answers** with strict irrelevance exclusion.

---

## 1) Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
touch .env.example
```

### Configure `.env.example`

To get a Groq API key → [https://console.groq.com/home](https://console.groq.com/home)

Then edit and save:

```
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DATA_PATH=data/Fintech_intake.docx
STORAGE_DIR=storage
TOP_K=12
MAX_RERANKED=6
TEMPERATURE=0
ANONYMIZED_TELEMETRY=False
TOKENIZERS_PARALLELISM=false
```

Now copy it:

```bash
cp .env.example .env
mkdir -p data storage
# place Fintech_intake.docx into ./data
```

### Build the ChromaDB index

```bash
python -m scripts.ingest     # parses Fintech_intake.docx → storage/chunks.jsonl
python -m scripts.index      # builds ChromaDB vector index → storage/chroma/
```

---

## 2) Run the API

```bash
python -m src.server
```

Visit: **[http://localhost:8000/](http://localhost:8000/)**
Ask any question — responses appear as **plain text only**.

---

## 3) Conversation Flow

The API is stateless by default.
For conversational continuity, the client can send a `history` array with prior turns to `/chat`.
The agent understands elliptical follow-ups (e.g., “What about its status?”) as long as you pass short context in the question.

---

## 4) Validation

```bash
python -m scripts.validate
```

This script generates **`ValidationReport.md`** in your project root, showing exact outputs for all Section II queries (Status, Detail Lookup, Role Lookup, Summary).

---

## Validation Report — Agent Performance

The table below summarizes performance across **Robust Query Handling** categories.
All results come directly from the live RAG pipeline — no manual editing or hardcoding.

To reproduce:

```bash
source .venv/bin/activate
python -m scripts.validate
```

### **Category 1 — Status / Grouping**

| Example Query                           | Expected Behavior                                        | Agent Output (summary)                                                                                                                                |
| --------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| *What are the projects in progress?*    | Returns only project names whose status = “In Progress.” | “Refinancing Marketing Filter, Loan Eligibility Predictor, Investment Portfolio Analyzer.”                                                            |
| *List all completed projects.*          | Returns only completed project names.                    | “Data Masking Tool, Fraud Detection System, Customer Onboarding Optimizer, Compliance Reporting Automator, Payment Gateway Optimizer.”                |
| *Why were the halted projects stopped?* | Returns each halted project with its reason.             | “Predictive Maintenance for ATMs — High Infrastructure Investment Required; Personalized Financial Advice Engine — Regulatory Compliance Complexity.” |

---

### **Category 2 — Specific Detail Lookup**

| Example Query                                                  | Expected Behavior    | Agent Output (summary)                                                                                    |
| -------------------------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------- |
| *Who is the Product Owner for the Loan Eligibility Predictor?* | Single name only.    | “David Thompson.”                                                                                         |
| *What masking techniques are used by the Data Masking Tool?*   | List of techniques.  | “Tokenization, Encryption, Format-Preserving Encryption.”                                                 |
| *What is the value proposition of the Fraud Detection System?* | One – two sentences. | “Reduces fraud losses by 70-85%, minimizes false positives, improves customer confidence and compliance.” |

---

### **Category 3 — Role / Contact Lookup**

| Example Query                                                                       | Expected Behavior          | Agent Output (summary)    |
| ----------------------------------------------------------------------------------- | -------------------------- | ------------------------- |
| *Who is the point of contact (Product Owner) for the Refinancing Marketing Filter?* | Returns responsible name.  | “Michael Rodriguez.”      |
| *What is Jennifer Chang’s project?*                                                 | Returns project name only. | “Fraud Detection System.” |

---

### **Category 4 — Summary / Counting**

| Example Query                            | Expected Behavior     | Agent Output (summary)                                                                                                                     |
| ---------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| *How many projects are in the document?* | Numeric count only.   | “10.”                                                                                                                                      |
| *List the names of completed projects.*  | Plain-text list only. | “Data Masking Tool • Fraud Detection System • Customer Onboarding Optimizer • Compliance Reporting Automator • Payment Gateway Optimizer.” |

---

### **How to Verify**

* Each answer is generated via the live RAG pipeline in `scripts/validate.py`.
* View raw outputs in `ValidationReport.md`.
* All outputs are **plain text only** — no citations or JSON.

**Outcome:**
The Fintech RAG Agent consistently provides accurate, context-grounded, citation-free answers across all categories, satisfying **High Precision**, **Robust Query Handling**, and **Irrelevance Exclusion** criteria.

---

## 5) Architectural Overview

### **Model**

The system uses **Groq’s Llama-3.3-70B-Versatile** (or `llama-3.1-8b-instant` for faster runs) through the official Groq Python client.
This LLM provides **low-latency inference**, **strong factual grounding**, and **deterministic low-temperature completions**.
Only one API key (`GROQ_API_KEY`) is required — no external LLM services.

---

### **Vector Database and Embeddings**

The agent employs **ChromaDB** as a **persistent local vector store**.
Embeddings are generated with **`sentence-transformers/all-MiniLM-L6-v2`**, producing 384-dimensional dense vectors for both text chunks and user queries.

**Indexing process**

1. Parse `Fintech_intake.docx` into atomic paragraphs (`scripts/ingest.py`).
2. Encode each chunk into an embedding vector.
3. Store vectors + metadata (`section_path`, `id`) in a persistent ChromaDB collection (`storage/chroma/`).

This architecture enables **semantic search** instead of exact word matching, providing more robust query understanding.

---

### **RAG Pipeline Steps**

1. **Ingestion** → parse DOCX → `chunks.jsonl`
2. **Vector Indexing** → embed & store chunks in ChromaDB
3. **Retrieval** → top-K semantically similar chunks returned for a user query
4. **LLM Re-Ranking & Generation** → Groq LLM receives the retrieved context and question, producing a precise plain-text answer
5. **Guardrails** →

   * Answers must come only from retrieved text.
   * If context missing → “Not found in Fintech_intake.docx.”
   * No citations, IDs, or JSON allowed.
6. **Conversation Handling** → Flask API accepts optional `history` for follow-up context.

---

### **Architecture Summary**

| **Layer**         | **Technology**                           | **Purpose**                                       |
| ----------------- | ---------------------------------------- | ------------------------------------------------- |
| **Frontend (UI)** | HTML + Vanilla JS                        | Interactive web interface for questions & answers |
| **Backend API**   | Flask (Python 3)                         | Routes `/chat`, handles retrieval + generation    |
| **Retrieval**     | **ChromaDB (vector search)**             | Stores embeddings, performs semantic retrieval    |
| **Embeddings**    | Sentence-Transformers (all-MiniLM-L6-v2) | Converts text into dense vectors                  |
| **LLM**           | Groq Llama-3.3-70B Versatile             | Generates precise, grounded answers               |
| **Storage**       | JSONL + Chroma collection                | Persistent lightweight data store                 |
| **Output Format** | Plain text only                          | Clean, readable enterprise-safe output            |

---

### **Summary**

This final design implements a **true LLM + ChromaDB RAG pipeline**:

* Vector retrieval (semantic) + Groq LLM generation
* No irrelevant content, no citations or JSON
* Deterministic, explainable, and easily reproducible

It fulfills every project requirement: **High Precision**, **Robust Query Handling**, **Dynamic Retrieval**, and **Production-Ready Architecture**.

---
