"""
Knowledge base retrieval module.
Implements keyword-based retrieval with optional ChromaDB/RAG support.
"""

import os
import re
import math
from pathlib import Path
from typing import List, Tuple, Optional
from collections import defaultdict

from schemas import Source

# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

KB_DIR = Path(__file__).parent / "knowledge_base"

_DOCS: List[dict] = []  # list of {title, document, category, text, chunks}


def _load_documents() -> List[dict]:
    docs = []
    for fpath in sorted(KB_DIR.glob("*.txt")):
        text = fpath.read_text(encoding="utf-8")
        # Parse header
        title = fpath.stem
        doc_id = fpath.stem
        category = ""
        for line in text.splitlines()[:6]:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("DOCUMENT:"):
                doc_id = line.replace("DOCUMENT:", "").strip()
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()
        docs.append({
            "title": title,
            "document": doc_id,
            "category": category,
            "text": text,
            "file": fpath.name,
        })
    return docs


def get_documents() -> List[dict]:
    global _DOCS
    if not _DOCS:
        _DOCS = _load_documents()
    return _DOCS


# ---------------------------------------------------------------------------
# Keyword-based TF-IDF style retrieval
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def _build_idf(docs: List[dict]) -> dict:
    N = len(docs)
    df = defaultdict(int)
    for doc in docs:
        tokens = set(_tokenize(doc["text"]))
        for t in tokens:
            df[t] += 1
    return {t: math.log((N + 1) / (cnt + 1)) + 1 for t, cnt in df.items()}


_IDF: dict = {}


def _score_doc(query_tokens: List[str], doc: dict, idf: dict) -> float:
    doc_tokens = _tokenize(doc["text"])
    doc_freq = defaultdict(int)
    for t in doc_tokens:
        doc_freq[t] += 1
    score = 0.0
    for qt in query_tokens:
        tf = doc_freq.get(qt, 0)
        if tf > 0:
            tf_norm = 1 + math.log(tf)
            score += tf_norm * idf.get(qt, 1.0)
    # Boost by category match
    cat_tokens = set(_tokenize(doc["category"]))
    for qt in query_tokens:
        if qt in cat_tokens:
            score += 5.0
    return score


def retrieve(query: str, top_k: int = 2) -> List[Tuple[dict, float]]:
    """Return top_k (doc, score) tuples for the given query."""
    docs = get_documents()
    if not docs:
        return []
    global _IDF
    if not _IDF:
        _IDF = _build_idf(docs)
    query_tokens = _tokenize(query)
    scores = [(doc, _score_doc(query_tokens, doc, _IDF)) for doc in docs]
    scores.sort(key=lambda x: x[1], reverse=True)
    # Filter out zero-score docs
    results = [(doc, score) for doc, score in scores[:top_k] if score > 0]
    return results


def retrieve_sources(query: str, top_k: int = 2) -> List[Source]:
    results = retrieve(query, top_k=top_k)
    max_score = max((s for _, s in results), default=1.0) or 1.0
    sources = []
    for doc, score in results:
        sources.append(Source(
            title=doc["title"],
            document=doc["document"],
            relevance=round(score / max_score, 3),
        ))
    return sources


def get_relevant_text(query: str, top_k: int = 1) -> Optional[str]:
    results = retrieve(query, top_k=top_k)
    if results:
        return results[0][0]["text"]
    return None


# ---------------------------------------------------------------------------
# ChromaDB / RAG (optional) — gracefully disabled if unavailable
# ---------------------------------------------------------------------------

RAG_AVAILABLE = False

try:
    import chromadb  # type: ignore
    from chromadb.utils import embedding_functions  # type: ignore

    _chroma_client = None
    _chroma_collection = None

    def _init_chroma():
        global _chroma_client, _chroma_collection, RAG_AVAILABLE
        try:
            _chroma_client = chromadb.Client()
            ef = embedding_functions.DefaultEmbeddingFunction()
            _chroma_collection = _chroma_client.get_or_create_collection(
                name="iot_kb", embedding_function=ef
            )
            docs = get_documents()
            existing_ids = set(_chroma_collection.get()["ids"])
            for doc in docs:
                if doc["document"] not in existing_ids:
                    _chroma_collection.add(
                        documents=[doc["text"]],
                        ids=[doc["document"]],
                        metadatas=[{"title": doc["title"], "category": doc["category"]}],
                    )
            RAG_AVAILABLE = True
        except Exception:
            RAG_AVAILABLE = False

    _init_chroma()

except ImportError:
    pass
