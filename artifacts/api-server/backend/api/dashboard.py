from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    Document as DocumentModel,
    Review, QARun, AuditRun, DiagramArtifact, ADRRecord
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_documents = db.query(func.count(DocumentModel.id)).filter(
        DocumentModel.is_kb == False
    ).scalar() or 0

    total_reviews = db.query(func.count(Review.id)).scalar() or 0

    total_kb_documents = db.query(func.count(DocumentModel.id)).filter(
        DocumentModel.is_kb == True
    ).scalar() or 0

    total_qa_runs = db.query(func.count(QARun.id)).scalar() or 0

    needs_review_count = (
        db.query(func.count(Review.id)).filter(Review.needs_review == True).scalar() or 0
    ) + (
        db.query(func.count(QARun.id)).filter(QARun.needs_review == True).scalar() or 0
    )

    total_audit_runs = db.query(func.count(AuditRun.id)).scalar() or 0

    error_count = db.query(func.count(AuditRun.id)).filter(
        AuditRun.status == "error"
    ).scalar() or 0

    avg_ms = db.query(func.avg(AuditRun.duration_ms)).scalar() or 0.0

    total_diagrams = db.query(func.count(DiagramArtifact.id)).scalar() or 0

    total_adr = db.query(func.count(ADRRecord.id)).scalar() or 0

    recent_errors = db.query(AuditRun).filter(
        AuditRun.status == "error"
    ).order_by(AuditRun.created_at.desc()).limit(5).all()

    def audit_dict(a: AuditRun):
        return {
            "id": a.id,
            "created_at": a.created_at.isoformat() + "Z",
            "action": a.action,
            "input": a.input,
            "output": a.output,
            "status": a.status,
            "error": a.error,
            "duration_ms": a.duration_ms,
        }

    return {
        "total_documents": total_documents,
        "total_reviews": total_reviews,
        "total_kb_documents": total_kb_documents,
        "total_qa_runs": total_qa_runs,
        "needs_review_count": needs_review_count,
        "total_audit_runs": total_audit_runs,
        "error_count": error_count,
        "avg_duration_ms": float(avg_ms),
        "total_diagrams": total_diagrams,
        "total_adr_records": total_adr,
        "recent_errors": [audit_dict(e) for e in recent_errors],
    }


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    runs = db.query(AuditRun).order_by(AuditRun.created_at.desc()).limit(limit).all()

    action_labels = {
        "review": "Создана рецензия",
        "direct_ai_review": "Прямая AI-рецензия",
        "kb_ask": "Вопрос к базе знаний",
        "direct_ai_answer": "Прямой ответ AI",
        "generate_urs": "Генерация URS",
        "generate_srs": "Генерация SRS",
        "generate_adr": "Генерация ADR",
        "design_api": "Дизайн API",
        "recommend_architecture": "Рекомендация архитектуры",
        "generate_diagrams": "Генерация диаграмм",
        "generate_c4": "Генерация C4",
        "generate_uml": "Генерация UML",
        "generate_erd": "Генерация ERD",
    }

    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat() + "Z",
            "action": r.action,
            "status": r.status,
            "description": action_labels.get(r.action, r.action),
            "needs_review": r.status == "needs_review",
            "duration_ms": r.duration_ms,
        }
        for r in runs
    ]
