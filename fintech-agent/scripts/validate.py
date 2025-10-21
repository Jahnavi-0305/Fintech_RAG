
# -*- coding: utf-8 -*-
import datetime as dt, orjson as json
from src.retriever import BM25Retriever
from src.agent import rerank_chunks, answer
from src.config import BM25_PATH, CHUNKS_PATH, TOP_K


TESTS = [
    {"q": "Team Members for Data Masking Tool — return only names"},
    {"q": "Product Owner for Fraud Detection System"},
    {"q": "Status for Predictive Maintenance for ATMs"},
    {"q": "Reason for Personalized Financial Advice Engine"},
    {"q": "Business Objective for Compliance Reporting Automator"},
    {"q": "Value Proposition for Payment Gateway Optimizer"},
    {"q": "Team Members for Loan Eligibility Predictor — only names"},
    {"q": "Who is the Product Owner for Refinancing Marketing Filter?"},
    {"q": "What is the status for Investment Portfolio Analyzer?"},
    {"q": "List Team Members for Customer Onboarding Optimizer — only names"},
]

if __name__ == "__main__":
    retriever = BM25Retriever.load(BM25_PATH, CHUNKS_PATH)
    out = ["# Validation Report", f"Run: {dt.datetime.utcnow().isoformat()}Z", ""]
    for t in TESTS:
        q = t["q"]
        retrieved = retriever.retrieve(q, TOP_K)
        selected = rerank_chunks(q, retrieved)
        res = answer(q, selected)
        out += [f"## Q: {q}", "", "**Answer**:", ""]
        ans = res["answer"]
        if isinstance(ans, dict):
            out.append(json.dumps(ans, option=json.OPT_INDENT_2).decode())
        else:
            out.append(ans)
        out += ["", f"**Used Chunks**: {res['used_chunks']}", "\n---\n"]
    with open("ValidationReport.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Wrote ValidationReport.md")
