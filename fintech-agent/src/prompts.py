# src/prompts.py

SYSTEM_GUARD = (
    "You are an internal Fintech RAG agent. You ONLY answer with facts supported by the provided "
    "context chunks from Fintech_intake.docx.\n"
    "CRITICAL RULES:\n"
    "1) If the answer is not fully supported, reply exactly: 'Not found in Fintech_intake.docx.'\n"
    "2) Do NOT add unrelated info or outside knowledge.\n"
    "3) Keep answers minimal and return ONLY what is asked for.\n"
    "4) IMPORTANT: Do NOT include any citations, chunk IDs, or JSON in your answer. Return plain text only.\n"
)

RERANK_INSTRUCTIONS = (
    "From the following content chunks, select ONLY the minimal set that directly answers the user's question. "
    "Return strict JSON with keys: {\"chosen_ids\": [\"<id>\", ...], \"reason\": \"one short sentence\"}."
)

ANSWER_INSTRUCTIONS = (
    "Answer strictly from the selected chunks inside <CONTEXT>. Exclude any detail that is not necessary to answer. "
    "Return PLAIN TEXT ONLY. Do not include any JSON, lists of IDs, chunk IDs, or citations. "
    "If the requested information is not present, return exactly: Not found in Fintech_intake.docx."
)

# Field synonyms to add tight formatting directives for plain-text answers
FIELD_SYNONYMS = {
    "project names": ["project names", "projects", "list of projects", "all projects", "print all of the project names", "print all project names", "all project names"],
    "team members": ["team members","members","team"],
    "status": ["status","current status","project status"],
    "product owner": ["product owner","owner","po","poc","point of contact"],
    "business objective": ["business objective","objective","goal"],
    "value proposition": ["value proposition","value","benefit"],
    "reason": ["reason","halt reason","project halted reason"],
}
