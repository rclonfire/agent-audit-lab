"""Keyword-frequency retrieval over the markdown knowledge base.

Deliberately simple: score = term frequency in the body, plus a 3x weight for
title hits. This is the retrieval layer many teams actually ship first, and it
carries seeded defect D3: intent synonyms ("cancel my subscription") lose to
keyword-rich articles about a different task. See company/DEFECTS.md.
"""

import re
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "kb"

STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in",
    "is", "it", "my", "of", "on", "or", "the", "to", "what", "when", "where",
    "with", "you", "your",
}


def _tokens(text: str):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def load_kb():
    docs = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text()
        title = text.splitlines()[0].lstrip("# ").strip() if text else path.stem
        docs.append({"file": path.name, "title": title, "text": text})
    return docs


def retrieve(query: str, k: int = 2):
    q = _tokens(query)
    scored = []
    for doc in load_kb():
        body_tf = _tokens(doc["text"])
        title_tf = _tokens(doc["title"])
        score = sum(body_tf.count(t) for t in q) + 3 * sum(title_tf.count(t) for t in q)
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda s: -s[0])
    return [{"file": d["file"], "title": d["title"], "text": d["text"], "score": s}
            for s, d in scored[:k]]
