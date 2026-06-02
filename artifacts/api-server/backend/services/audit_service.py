import json
import time
import logging
from typing import Any, Callable, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def save_audit(
    db: Session,
    action: str,
    input_data: Any,
    output_data: Any,
    status: str,
    duration_ms: int,
    error: Optional[str] = None,
):
    from backend.models import AuditRun
    try:
        audit = AuditRun(
            action=action,
            input=json.dumps(input_data, ensure_ascii=False, default=str) if input_data is not None else None,
            output=json.dumps(output_data, ensure_ascii=False, default=str) if output_data is not None else None,
            status=status,
            error=str(error)[:500] if error else None,
            duration_ms=duration_ms,
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save audit run: {e}")


def with_audit(db: Session, action: str, input_data: Any, func: Callable) -> Any:
    start = time.time()
    try:
        result = func()
        duration_ms = int((time.time() - start) * 1000)
        status = "needs_review" if (isinstance(result, dict) and result.get("needs_review")) else "ok"
        save_audit(db, action, input_data, result, status, duration_ms)
        return result
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        save_audit(db, action, input_data, None, "error", duration_ms, error=str(e))
        raise
