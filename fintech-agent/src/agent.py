# src/agent.py
from typing import List, Dict, Optional
from groq import Groq
import json as pyjson
import regex as re

from .config import GROQ_API_KEY, GROQ_MODEL, MAX_RERANKED, TEMPERATURE
from .prompts import SYSTEM_GUARD, RERANK_INSTRUCTIONS, ANSWER_INSTRUCTIONS, FIELD_SYNONYMS

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def chat(messages, json_mode: bool = False):
    kwargs = {"temperature": TEMPERATURE}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    return client.chat.completions.create(model=GROQ_MODEL, messages=messages, **kwargs)

def detect_requested_field(question: str) -> Optional[str]:
    q = (question or "").lower()
    for canonical, syns in FIELD_SYNONYMS.items():
        for s in syns:
            if re.search(rf"\b{re.escape(s)}\b", q):
                return canonical
    return None

def rerank_chunks(question: str, retrieved: List[Dict]) -> List[Dict]:
    # Provide compact catalog for selection
    catalog = [{"id": c["id"], "section": c["section_path"], "text": c["text"][:1200]} for c in retrieved]
    resp = chat(
        [
            {"role": "system", "content": SYSTEM_GUARD},
            {
                "role": "user",
                "content": f"Question: {question}\n{RERANK_INSTRUCTIONS}\nChunks: {pyjson.dumps(catalog)}",
            },
        ],
        json_mode=True,
    )
    try:
        data = pyjson.loads(resp.choices[0].message.content)
        chosen = set(data.get("chosen_ids", []))
        picked = [c for c in retrieved if c["id"] in chosen]
        if not picked:
            picked = retrieved[:MAX_RERANKED]
        return picked
    except Exception:
        return retrieved[:MAX_RERANKED]

def _context_block(selected: List[Dict]) -> str:
    # NOTE: we include chunk IDs in context for the model, but we instruct it NOT to echo them.
    return "\n\n".join([f"[{c['id']}] ({c['section_path']})\n{c['text']}" for c in selected])

def _field_directive(field: Optional[str]) -> str:
    if not field:
        return ""
    # Plain-text only formatting for each field
    if field == "project names":
        return "Return ONLY the project names, one per line. No bullets, no numbering, no JSON, no citations."
    if field == "team members":
        return "Return ONLY the team member names, one per line. No bullets, no JSON, no citations."
    if field == "product owner":
        return "Return ONLY the product owner's full name as plain text. No JSON, no citations."
    if field == "status":
        return "Return ONLY the project status as plain text. No JSON, no citations."
    if field == "business objective":
        return "Return ONLY the business objective as plain text. No JSON, no citations."
    if field == "value proposition":
        return "Return ONLY the value proposition as plain text. No JSON, no citations."
    if field == "reason":
        return "Return ONLY the reason as plain text. No JSON, no citations."
    return ""

def answer(question: str, selected: List[Dict], history: Optional[List[Dict]] = None) -> Dict:
    """
    Always return a plain-text answer string in the 'answer' field.
    No JSON payloads, no citations, no chunk IDs.
    """
    field = detect_requested_field(question)
    context = _context_block(selected)
    hist = history or []
    messages = [{"role": "system", "content": SYSTEM_GUARD}]
    messages.extend(hist)
    messages.append(
        {
            "role": "user",
            "content": (
                f"{ANSWER_INSTRUCTIONS}\n"
                f"{_field_directive(field)}\n\n"
                f"<CONTEXT>\n{context}\n</CONTEXT>\n\n"
                f"<QUESTION>\n{question}\n</QUESTION>"
            ),
        }
    )

    # Force normal (text) mode for outputs; we don't want JSON back
    resp = chat(messages, json_mode=False)
    content = resp.choices[0].message.content or ""

    # Strip any accidental inline [chunk_id]s the model might include
    content = re.sub(r"\s*\[[0-9a-fA-F]{8}\]", "", content).strip()

    # Ensure single newline-separated list if model tries to add bullets/numbers
    # (we don't enforce this globally; only when field suggests a list)
    if field in {"project names", "team members"}:
        # Convert common bullet/number patterns to plain lines
        lines = []
        for line in content.splitlines():
            line = re.sub(r"^\s*[-•\d\.\)]\s*", "", line).strip()
            if line:
                lines.append(line)
        content = "\n".join(lines)

    return {"answer": content}
