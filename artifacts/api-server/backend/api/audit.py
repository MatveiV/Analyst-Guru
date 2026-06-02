import json
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import AuditRun

router = APIRouter(prefix="/api/audit", tags=["audit"])


def audit_to_dict(a: AuditRun) -> dict:
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


@router.get("")
def list_audit_runs(
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(AuditRun)
    if action:
        q = q.filter(AuditRun.action == action)
    if status:
        q = q.filter(AuditRun.status == status)
    runs = q.order_by(AuditRun.created_at.desc()).offset(offset).limit(limit).all()
    return [audit_to_dict(r) for r in runs]
