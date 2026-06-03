import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import Document as DocumentModel, QARun
from backend.services import ai_service, rag_engine, audit_service

router = APIRouter(prefix="/api/kb", tags=["kb"])


class KbDocumentInput(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    text: str = Field(min_length=10, max_length=30000)
    doc_type: str = "kb_article"
    project_name: Optional[str] = None


class KbQuestionInput(BaseModel):
    question: str = Field(min_length=5, max_length=2000)


class DirectAnswerInput(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    context: str = Field(min_length=0, max_length=50000)


def doc_to_dict(doc: DocumentModel) -> dict:
    return {
        "id": doc.id,
        "created_at": doc.created_at.isoformat() + "Z",
        "title": doc.title,
        "text": doc.text,
        "doc_type": doc.doc_type,
        "project_name": doc.project_name,
        "is_kb": doc.is_kb,
    }


@router.get("/documents")
def list_kb_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentModel).filter(
        DocumentModel.is_kb == True
    ).order_by(DocumentModel.created_at.desc()).all()
    return [doc_to_dict(d) for d in docs]


@router.post("/documents", status_code=201)
def add_kb_document(body: KbDocumentInput, db: Session = Depends(get_db)):
    doc = DocumentModel(
        title=body.title,
        text=body.text,
        doc_type=body.doc_type,
        project_name=body.project_name,
        is_kb=True,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Index for RAG
    try:
        rag_engine.index_document(db, doc.id, doc.text)
    except Exception:
        pass

    return {"status": "ok", "document_id": doc.id, **doc_to_dict(doc)}


@router.post("/ask")
def ask_knowledge_base(body: KbQuestionInput, db: Session = Depends(get_db)):
    search_results = rag_engine.search_kb(db, body.question)
    context = rag_engine.format_context(search_results)

    def do_answer():
        return ai_service.answer_with_sources(body.question, context)

    result = audit_service.with_audit(
        db, "kb_ask", {"question": body.question}, do_answer
    )

    sources = result.get("sources", [])
    # Enrich sources with document titles from search results
    if not sources and search_results:
        sources = [{"quote": r["text"][:300], "document_id": r["document_id"], "document_title": r["document_title"]}
                   for r in search_results[:3]]

    # Map document ids to titles
    enriched_sources = []
    for s in sources:
        enriched = {"quote": s.get("quote", ""), "document_id": None, "document_title": None}
        for sr in search_results:
            if s.get("quote", "")[:50] in sr["text"]:
                enriched["document_id"] = sr["document_id"]
                enriched["document_title"] = sr["document_title"]
                break
        enriched_sources.append(enriched)

    needs_review = result.get("needs_review", not bool(search_results))

    qa = QARun(
        question=body.question,
        answer=result.get("answer", ""),
        sources_json=json.dumps(enriched_sources, ensure_ascii=False),
        needs_review=needs_review,
        error=result.get("error"),
    )
    db.add(qa)
    db.commit()
    db.refresh(qa)

    return {
        "id": qa.id,
        "created_at": qa.created_at.isoformat() + "Z",
        "question": qa.question,
        "answer": qa.answer,
        "sources": enriched_sources,
        "needs_review": qa.needs_review,
        "error": qa.error,
    }


@router.get("/history")
def list_kb_history(
    needs_review: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(QARun)
    if needs_review is not None:
        q = q.filter(QARun.needs_review == needs_review)
    runs = q.order_by(QARun.created_at.desc()).limit(limit).all()
    result = []
    for run in runs:
        try:
            sources = json.loads(run.sources_json)
        except Exception:
            sources = []
        result.append({
            "id": run.id,
            "created_at": run.created_at.isoformat() + "Z",
            "question": run.question,
            "answer": run.answer,
            "sources_json": sources,
            "needs_review": run.needs_review,
            "error": run.error,
        })
    return result


router_direct = APIRouter(prefix="/api/ai", tags=["kb"])


@router_direct.post("/answer_with_sources")
def direct_answer(body: DirectAnswerInput, db: Session = Depends(get_db)):
    def do_answer():
        return ai_service.answer_with_sources(body.question, body.context)

    return audit_service.with_audit(
        db, "direct_ai_answer", {"question": body.question}, do_answer
    )
