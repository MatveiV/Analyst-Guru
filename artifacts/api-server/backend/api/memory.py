import json
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import MemoryItem

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryItemInput(BaseModel):
    memory_type: str
    content: str = Field(min_length=1)
    tags: Optional[List[str]] = []
    project_name: Optional[str] = None


class MemorySearchInput(BaseModel):
    query: str = Field(min_length=1)
    memory_type: Optional[str] = None
    limit: int = 10


def mem_to_dict(m: MemoryItem) -> dict:
    try:
        tags = json.loads(m.tags) if m.tags else []
    except Exception:
        tags = []
    return {
        "id": m.id,
        "created_at": m.created_at.isoformat() + "Z",
        "memory_type": m.memory_type,
        "content": m.content,
        "tags": tags,
        "project_name": m.project_name,
        "relevance_score": m.relevance_score,
    }


@router.post("/store", status_code=201)
def store_memory(body: MemoryItemInput, db: Session = Depends(get_db)):
    item = MemoryItem(
        memory_type=body.memory_type,
        content=body.content,
        tags=json.dumps(body.tags or [], ensure_ascii=False),
        project_name=body.project_name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return mem_to_dict(item)


@router.post("/search")
def search_memory(body: MemorySearchInput, db: Session = Depends(get_db)):
    q = db.query(MemoryItem)
    if body.memory_type:
        q = q.filter(MemoryItem.memory_type == body.memory_type)

    words = [w.lower() for w in body.query.split() if len(w) > 2]
    if words:
        conditions = [MemoryItem.content.ilike(f"%{w}%") for w in words]
        q = q.filter(or_(*conditions))

    items = q.order_by(MemoryItem.created_at.desc()).limit(body.limit).all()
    return [mem_to_dict(i) for i in items]


@router.get("/recent")
def get_recent_memory(
    memory_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(MemoryItem)
    if memory_type:
        q = q.filter(MemoryItem.memory_type == memory_type)
    items = q.order_by(MemoryItem.created_at.desc()).limit(limit).all()
    return [mem_to_dict(i) for i in items]


@router.post("/consolidate")
def consolidate_memory(db: Session = Depends(get_db)):
    all_items = db.query(MemoryItem).all()
    total_before = len(all_items)

    seen = set()
    duplicates = []
    for item in all_items:
        key = (item.memory_type, item.content[:100].lower())
        if key in seen:
            duplicates.append(item)
        else:
            seen.add(key)

    for dup in duplicates:
        db.delete(dup)
    db.commit()

    total_after = total_before - len(duplicates)
    return {
        "deduplicated": len(duplicates),
        "merged": 0,
        "total_before": total_before,
        "total_after": total_after,
    }
