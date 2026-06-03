import json
import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import Document as DocumentModel, Review as ReviewModel
from backend.services import ai_service, audit_service

router = APIRouter(prefix="/api", tags=["reviews"])


class DirectReviewInput(BaseModel):
    text: str = Field(min_length=1, max_length=30000)


def review_to_dict(review: ReviewModel, doc_title: Optional[str] = None) -> dict:
    try:
        rj = json.loads(review.review_json)
    except Exception:
        rj = {}
    return {
        "id": review.id,
        "created_at": review.created_at.isoformat() + "Z",
        "document_id": review.document_id,
        "review_json": rj,
        "needs_review": review.needs_review,
        "confidence": review.confidence,
        "error": review.error,
        "document_title": doc_title,
    }


@router.post("/documents/{id}/review", status_code=201)
def review_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Gather memory context
    from backend.models import MemoryItem
    risks = db.query(MemoryItem).filter(MemoryItem.memory_type == "risk").limit(5).all()
    lessons = db.query(MemoryItem).filter(MemoryItem.memory_type == "episodic").limit(5).all()
    decisions = db.query(MemoryItem).filter(MemoryItem.memory_type == "decision").limit(5).all()

    memory_risks = "; ".join(r.content[:200] for r in risks) if risks else ""
    memory_lessons = "; ".join(r.content[:200] for r in lessons) if lessons else ""
    memory_decisions = "; ".join(r.content[:200] for r in decisions) if decisions else ""

    def do_review():
        return ai_service.review_document(
            doc.text,
            memory_risks=memory_risks,
            memory_lessons=memory_lessons,
            memory_decisions=memory_decisions,
        )

    result = audit_service.with_audit(
        db, "review", {"document_id": id, "title": doc.title}, do_review
    )

    review = ReviewModel(
        document_id=id,
        review_json=json.dumps(result, ensure_ascii=False),
        needs_review=result.get("needs_review", False),
        confidence=result.get("confidence", "low"),
        error=result.get("error"),
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Store risks and lessons in memory
    if result.get("needs_review") is False:
        from backend.models import MemoryItem
        for risk in result.get("risks", []):
            mem = MemoryItem(
                memory_type="risk",
                content=f"[{risk.get('severity', 'medium').upper()}] {risk.get('description', '')}",
                tags=json.dumps(["auto-extracted", doc.doc_type]),
                project_name=doc.project_name,
            )
            db.add(mem)
        for lesson in result.get("lessons_learned", []):
            mem = MemoryItem(
                memory_type="episodic",
                content=lesson,
                tags=json.dumps(["auto-extracted"]),
                project_name=doc.project_name,
            )
            db.add(mem)
        db.commit()

    return {"status": "ok", "review_id": review.id, **review_to_dict(review, doc.title)}


@router.get("/reviews")
def list_reviews(
    needs_review: Optional[bool] = Query(None),
    confidence: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(ReviewModel, DocumentModel).join(
        DocumentModel, ReviewModel.document_id == DocumentModel.id
    )
    if needs_review is not None:
        q = q.filter(ReviewModel.needs_review == needs_review)
    if confidence:
        q = q.filter(ReviewModel.confidence == confidence)
    rows = q.order_by(ReviewModel.created_at.desc()).offset(offset).limit(limit).all()
    return [review_to_dict(r, d.title) for r, d in rows]


@router.get("/reviews/{id}")
def get_review(id: str, db: Session = Depends(get_db)):
    row = db.query(ReviewModel, DocumentModel).join(
        DocumentModel, ReviewModel.document_id == DocumentModel.id
    ).filter(ReviewModel.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    review, doc = row
    return review_to_dict(review, doc.title)


@router.post("/ai/review")
def direct_ai_review(body: DirectReviewInput, db: Session = Depends(get_db)):
    def do_review():
        return ai_service.review_document(body.text)

    result = audit_service.with_audit(
        db, "direct_ai_review", {"text_length": len(body.text)}, do_review
    )
    return result


@router.get("/reviews/{id}/export/json")
def export_review_json(id: str, db: Session = Depends(get_db)):
    review = db.query(ReviewModel).filter(ReviewModel.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    try:
        return json.loads(review.review_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse review JSON")


@router.get("/reviews/{id}/export/csv")
def export_review_csv(id: str, db: Session = Depends(get_db)):
    review = db.query(ReviewModel).filter(ReviewModel.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    try:
        rj = json.loads(review.review_json)
    except Exception:
        rj = {}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Section", "Item", "Value"])
    writer.writerow(["Summary", "-", rj.get("summary", "")])
    writer.writerow(["Confidence", "-", rj.get("confidence", "")])
    writer.writerow(["Needs Review", "-", str(rj.get("needs_review", False))])
    for risk in rj.get("risks", []):
        writer.writerow(["Risk", risk.get("severity", ""), risk.get("description", "")])
    for mr in rj.get("missing_requirements", []):
        writer.writerow(["Missing Requirement", "-", mr])
    for q in rj.get("questions_to_client", []):
        writer.writerow(["Question to Client", "-", q])
    for ac in rj.get("acceptance_criteria", []):
        writer.writerow(["Acceptance Criteria", "-", ac])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=review_{id}.csv"},
    )
