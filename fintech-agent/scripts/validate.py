 # -*- coding: utf-8 -*-
"""
Validation script for Fintech RAG Agent (Groq + ChromaDB)
Generates ValidationReport.md with plain-text answers for all query categories.
Now telemetry & parallelism warnings are fully disabled.
"""

import os
from datetime import datetime, timezone

# --- Disable noisy logs and telemetry ---
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# --- Imports ---
from src.retriever import ChromaRetriever
from src.agent import rerank_chunks, answer
from src.config import TOP_K

# ---- Example Queries (Section II categories) ----
TESTS = [
    # Status / Grouping
    {"section": "Status / Grouping", "q": "What are the projects in progress? Return only project names."},
    {"section": "Status / Grouping", "q": "List all completed projects. Return only project names."},
    {"section": "Status / Grouping", "q": "Why were the halted projects stopped? Return only reasons, one per line."},

    #Specific Detail Lookup
    {"section": "Specific Detail Lookup", "q": "Who is the Product Owner for the Loan Eligibility Predictor?"},
    {"section": "Specific Detail Lookup", "q": "What are the masking techniques used by the Data Masking Tool? Return only techniques, one per line."},
    {"section": "Specific Detail Lookup", "q": "What is the value proposition of the Fraud Detection System? Return only the value proposition."},

    #Role / Contact Lookup
    {"section": "Role / Contact Lookup", "q": "Who is the point of contact (Product Owner) for the Refinancing Marketing Filter?"},
    {"section": "Role / Contact Lookup", "q": "What is Jennifer Chang's project? Return only the project name."},

    #Summary / Counting
    {"section": "Summary / Counting", "q": "How many projects are in the document? Return only the number."},
    {"section": "Summary / Counting", "q": "List the names of the completed projects. Return only names, one per line."},
]

def run_one(query, retriever):
    """Run a single query through the RAG pipeline."""
    try:
        retrieved = retriever.retrieve(query, TOP_K)
        selected = rerank_chunks(query, retrieved)
        res = answer(query, selected)
        ans = res.get("answer", "").strip()
        if not ans:
            ans = "(empty response)"
        return ans
    except Exception as e:
        return f"❌ ERROR: {e}"

if __name__ == "__main__":
    retriever = ChromaRetriever()

    lines = []
    lines.append("# Validation Report — Fintech RAG Agent")
    lines.append(f"Run: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    current_section = None

    for t in TESTS:
        if t["section"] != current_section:
            current_section = t["section"]
            lines.append(f"## {current_section}")
            lines.append("")

        q = t["q"]
        ans = run_one(q, retriever)

        lines.append(f"**Q:** {q}")
        lines.append("")
        lines.append("**Answer (plain text):**")
        lines.append("")
        lines.append(ans)
        lines.append("\n---\n")

    with open("ValidationReport.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Wrote ValidationReport.md (clean, plain-text, no warnings)")
