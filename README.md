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



## 🏗️ Architectural Overview

### **Model**
The **Fintech RAG Agent** uses **Groq’s hosted Llama-3.3-70B-Versatile** model through the official Groq Python client.  
This large-language model provides:
- **Fast inference**
- **Strong factual grounding**
- **Deterministic, low-temperature completions** suitable for enterprise retrieval-augmented tasks.  

No other API keys or third-party services are required — the system runs entirely with a single **`GROQ_API_KEY`**.

---

### **Indexing and Retrieval**
Instead of an external vector database, the agent employs a **BM25 lexical retriever** built with the `rank-bm25` library.

During ingestion:
- The source document **`Fintech_intake.docx`** is parsed into semantically atomic text chunks.  
- Each chunk is annotated with its hierarchical section path.  
- All chunks are tokenized and indexed locally into a **BM25Okapi** object serialized to  
  `storage/bm25_index.pkl`.  

This design **eliminates dependency on any external vector store** while providing **high precision** for well-structured enterprise documents.

---

### **RAG Pipeline Steps**
1. **Ingestion** – The `.docx` file is read and converted into normalized text chunks (UUID-labeled) saved as `chunks.jsonl`.  
2. **Indexing** – BM25 builds a term-frequency inverse-document-frequency (TF-IDF) index for lexical retrieval.  
3. **Retrieval** – For each user query, the top-K most relevant chunks are retrieved based on lexical similarity.  
4. **LLM Re-Ranking** – The **Groq Llama-3 model** re-ranks these chunks by contextual relevance and selects the minimal subset needed to answer precisely.  
5. **Answer Generation** – The model is instructed with strict guardrails to generate **plain-text only answers** supported exclusively by the selected context.  
   - If information is missing, it responds:  
     > “Not found in Fintech_intake.docx.”  
   - The system omits all citations, IDs, or JSON wrappers to maintain a clean, natural-language output.  
6. **Conversation Handling** – The **Flask API** accepts an optional `history` array so follow-up questions inherit context for conversational continuity.

---

### **Architecture Summary**

| **Layer**          | **Technology**                   | **Purpose** |
|--------------------|----------------------------------|-------------|
| **Frontend (UI)**  | HTML + Vanilla JS                | User interface for asking questions and viewing plain-text answers |
| **Backend API**    | Flask (Python 3)                 | Serves `/chat` endpoint and renders the UI |
| **Retrieval**      | BM25Okapi index                  | Local, dependency-free document retrieval |
| **Generation**     | Groq Llama-3.3-70B-Versatile     | Factual, low-temperature text generation |
| **Storage**        | JSONL + Pickle                   | Lightweight persistence for chunks and index |
| **Output Format**  | Plain text only                  | Ensures precision and excludes irrelevant content |

---

### **Summary**
This architecture achieves a **production-ready, Groq-only RAG pipeline** that meets all precision, contextual relevance, and simplicity requirements while remaining **fully auditable and reproducible**.

