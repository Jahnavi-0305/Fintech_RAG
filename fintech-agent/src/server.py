from flask import Flask, request, jsonify, render_template
from .retriever import BM25Retriever
from .agent import rerank_chunks, answer
from .config import BM25_PATH, CHUNKS_PATH, TOP_K

app = Flask(__name__, static_folder="../static", template_folder="../templates")

# Load retriever once at startup
retriever = BM25Retriever.load(BM25_PATH, CHUNKS_PATH)

@app.route("/health", methods=["GET"])
def health():
    return {"ok": True}

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    history = data.get("history")  # optional list of {role,content}

    if not question:
        return jsonify({"error": "question is required"}), 400

    retrieved = retriever.retrieve(question, TOP_K)
    selected = rerank_chunks(question, retrieved)
    result = answer(question, selected, history=history)
    return jsonify(result)


# ---- New: simple web UI ----
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # located in ../templates/index.html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
