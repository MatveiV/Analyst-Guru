import os
import json
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "5"))
MIN_SNIPPET_LEN = 50
MAX_SNIPPET_LEN = 1000
OVERLAP = 100

_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded sentence-transformers model")
        except Exception as e:
            logger.warning(f"Could not load sentence-transformers: {e}. Using keyword search only.")
            _embedding_model = False
    return _embedding_model


def chunk_text(text: str) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if len(para) < MIN_SNIPPET_LEN:
            continue
        if len(para) <= MAX_SNIPPET_LEN:
            chunks.append(para)
        else:
            start = 0
            while start < len(para):
                end = min(start + MAX_SNIPPET_LEN, len(para))
                chunk = para[start:end]
                if len(chunk) >= MIN_SNIPPET_LEN:
                    chunks.append(chunk)
                start = end - OVERLAP
                if start >= len(para):
                    break
    return chunks


def embed_text(text: str) -> Optional[List[float]]:
    model = _get_embedding_model()
    if not model:
        return None
    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        logger.warning(f"Embedding error: {e}")
        return None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    try:
        import numpy as np
        a_arr = np.array(a)
        b_arr = np.array(b)
        dot = np.dot(a_arr, b_arr)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))
    except Exception:
        return 0.0


def index_document(db: Session, document_id: str, text: str):
    from backend.models import Snippet
    # Remove old snippets
    db.query(Snippet).filter(Snippet.document_id == document_id).delete()

    chunks = chunk_text(text)
    for chunk in chunks:
        embedding = embed_text(chunk)
        snippet = Snippet(
            document_id=document_id,
            snippet_text=chunk,
            embedding=json.dumps(embedding) if embedding else None,
        )
        db.add(snippet)
    db.commit()


def keyword_search(db: Session, query: str, top_k: int = RAG_TOP_K) -> List[Tuple[str, str, str]]:
    from backend.models import Snippet, Document
    query_lower = query.lower()
    words = [w for w in query_lower.split() if len(w) > 2]

    snippets = db.query(Snippet, Document).join(Document, Snippet.document_id == Document.id).filter(
        Document.is_kb == True
    ).all()

    scored = []
    for snippet, doc in snippets:
        text_lower = snippet.snippet_text.lower()
        score = sum(1 for w in words if w in text_lower)
        if score > 0:
            scored.append((score, snippet.snippet_text, snippet.document_id, doc.title))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [(s[1], s[2], s[3]) for s in scored[:top_k]]


def semantic_search(db: Session, query: str, top_k: int = RAG_TOP_K) -> List[Tuple[str, str, str]]:
    from backend.models import Snippet, Document
    query_embedding = embed_text(query)
    if query_embedding is None:
        return []

    snippets = db.query(Snippet, Document).join(Document, Snippet.document_id == Document.id).filter(
        Document.is_kb == True,
        Snippet.embedding != None
    ).all()

    scored = []
    for snippet, doc in snippets:
        if snippet.embedding:
            try:
                emb = json.loads(snippet.embedding)
                score = cosine_similarity(query_embedding, emb)
                scored.append((score, snippet.snippet_text, snippet.document_id, doc.title))
            except Exception:
                pass

    scored.sort(key=lambda x: x[0], reverse=True)
    return [(s[1], s[2], s[3]) for s in scored[:top_k]]


def hybrid_search(db: Session, query: str, top_k: int = RAG_TOP_K) -> List[Tuple[str, str, str]]:
    keyword_results = keyword_search(db, query, top_k=top_k * 2)
    semantic_results = semantic_search(db, query, top_k=top_k * 2)

    scores: dict = {}
    all_snippets: dict = {}

    max_kw = len(keyword_results) or 1
    for i, (text, doc_id, doc_title) in enumerate(keyword_results):
        key = text[:100]
        scores[key] = scores.get(key, 0) + 0.5 * (1 - i / max_kw)
        all_snippets[key] = (text, doc_id, doc_title)

    max_sem = len(semantic_results) or 1
    for i, (text, doc_id, doc_title) in enumerate(semantic_results):
        key = text[:100]
        scores[key] = scores.get(key, 0) + 0.5 * (1 - i / max_sem)
        all_snippets[key] = (text, doc_id, doc_title)

    sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
    return [all_snippets[k] for k in sorted_keys[:top_k]]


def search_kb(db: Session, query: str) -> List[dict]:
    results = hybrid_search(db, query, RAG_TOP_K)
    return [
        {"text": text, "document_id": doc_id, "document_title": doc_title}
        for text, doc_id, doc_title in results
    ]


def format_context(results: List[dict]) -> str:
    if not results:
        return ""
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"[{i}] (из документа: {r['document_title']})\n{r['text']}")
    return "\n\n".join(parts)
