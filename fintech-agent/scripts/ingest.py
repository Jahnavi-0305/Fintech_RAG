import docx, orjson as json, os, uuid, regex as re
from pathlib import Path
from src.config import DATA_PATH, STORAGE_DIR, CHUNKS_PATH

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def iter_docx_blocks(d):
    """
    Robust heading fallback:
    - Uses Word heading styles if present
    - Otherwise detects lines like '1. Title' or '2) Title' as section headers
    - Everything else becomes a paragraph block under the last seen section
    """
    section_stack = []
    last_section = "ROOT"

    for p in d.paragraphs:
        style = (p.style.name or "").lower()
        text = p.text.strip()
        if not text:
            continue

        # Prefer Word heading styles
        if style.startswith("heading"):
            m = re.findall(r"\d+", style)
            level = int(m[0]) if m else 1
            section_stack = section_stack[:level-1]
            section_stack.append(text)
            last_section = " > ".join(section_stack)
            continue

        # Fallback numeric headers
        if re.match(r"^\s*\d+[\.\)]\s+\S", text):
            section_stack = [re.sub(r"^\s*\d+[\.\)]\s+", "", text)]
            last_section = " > ".join(section_stack)
            continue

        yield {"section_path": last_section, "text": text}

if __name__ == "__main__":
    os.makedirs(STORAGE_DIR, exist_ok=True)
    d = docx.Document(DATA_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        for block in iter_docx_blocks(d):
            chunk = {
                "id": str(uuid.uuid4())[:8],
                "section_path": block["section_path"],
                "text": normalize(block["text"]),
            }
            f.write(json.dumps(chunk) + b"\n")
    print(f"Wrote chunks → {CHUNKS_PATH}")
