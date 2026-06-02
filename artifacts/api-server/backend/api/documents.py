import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import Document as DocumentModel

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentInput(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    text: str = Field(min_length=10, max_length=30000)
    doc_type: str = "tz"
    project_name: Optional[str] = None
    is_kb: bool = False


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


@router.get("")
def list_documents(
    doc_type: Optional[str] = Query(None),
    project_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(DocumentModel).filter(DocumentModel.is_kb == False)
    if doc_type:
        q = q.filter(DocumentModel.doc_type == doc_type)
    if project_name:
        q = q.filter(DocumentModel.project_name == project_name)
    docs = q.order_by(DocumentModel.created_at.desc()).offset(offset).limit(limit).all()
    return [doc_to_dict(d) for d in docs]


@router.post("", status_code=201)
def create_document(body: DocumentInput, db: Session = Depends(get_db)):
    doc = DocumentModel(
        title=body.title,
        text=body.text,
        doc_type=body.doc_type,
        project_name=body.project_name,
        is_kb=body.is_kb,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc_to_dict(doc)


@router.get("/{id}")
def get_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc_to_dict(doc)


@router.delete("/{id}", status_code=204)
def delete_document(id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
