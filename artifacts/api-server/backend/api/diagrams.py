import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models import Document as DocumentModel, DiagramArtifact
from backend.services import ai_service, audit_service

router = APIRouter(prefix="/api", tags=["diagrams"])


class DiagramInput(BaseModel):
    text: str = Field(min_length=10)
    diagram_types: Optional[List[str]] = None


def diag_to_dict(d: DiagramArtifact) -> dict:
    return {
        "id": d.id,
        "created_at": d.created_at.isoformat() + "Z",
        "document_id": d.document_id,
        "diagram_type": d.diagram_type,
        "notation": d.notation,
        "source_code": d.source_code,
        "needs_review": d.needs_review,
    }


def _build_diagram_set(document_id: str, result: dict, db: Session) -> dict:
    diagrams = []

    diagram_map = [
        ("c4_context", "plantuml"),
        ("c4_container", "plantuml"),
        ("c4_component", "plantuml"),
        ("use_case", "plantuml"),
        ("sequence", "plantuml"),
        ("class_diagram", "plantuml"),
        ("erd", "plantuml"),
        ("mermaid_flowchart", "mermaid"),
    ]

    type_name_map = {
        "c4_context": "c4_context",
        "c4_container": "c4_container",
        "c4_component": "c4_component",
        "use_case": "use_case",
        "sequence": "sequence",
        "class_diagram": "class",
        "erd": "erd",
        "mermaid_flowchart": "flowchart",
    }

    for field, notation in diagram_map:
        code = result.get(field, "")
        if code and len(code.strip()) > 10:
            diag = DiagramArtifact(
                document_id=document_id,
                diagram_type=type_name_map[field],
                notation=notation,
                source_code=code,
                needs_review=result.get("needs_review", False),
            )
            db.add(diag)
            db.flush()
            diagrams.append(diag_to_dict(diag))

    db.commit()

    return {
        "document_id": document_id,
        "diagrams": diagrams,
        "c4_context": result.get("c4_context"),
        "c4_container": result.get("c4_container"),
        "c4_component": result.get("c4_component"),
        "use_case": result.get("use_case"),
        "sequence": result.get("sequence"),
        "class_diagram": result.get("class_diagram"),
        "erd": result.get("erd"),
        "mermaid_flowchart": result.get("mermaid_flowchart"),
        "confidence": result.get("confidence", "medium"),
        "needs_review": result.get("needs_review", False),
    }


@router.post("/documents/{id}/generate-diagrams")
def generate_diagrams(id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    def do_gen():
        return ai_service.generate_diagrams(doc.text)

    result = audit_service.with_audit(db, "generate_diagrams", {"document_id": id}, do_gen)
    return _build_diagram_set(id, result, db)


@router.get("/diagrams/{id}")
def get_diagram(id: str, db: Session = Depends(get_db)):
    d = db.query(DiagramArtifact).filter(DiagramArtifact.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diag_to_dict(d)


@router.post("/diagrams/generate-c4")
def generate_c4(body: DiagramInput, db: Session = Depends(get_db)):
    def do_gen():
        return ai_service.generate_diagrams(body.text)

    result = audit_service.with_audit(db, "generate_c4", {"text_length": len(body.text)}, do_gen)

    # Use a synthetic document id for standalone generation
    import uuid
    fake_id = str(uuid.uuid4())
    doc = DocumentModel(id=fake_id, title="C4 Generation", text=body.text, doc_type="tz")
    db.add(doc)
    db.flush()

    return _build_diagram_set(fake_id, result, db)


@router.post("/diagrams/generate-uml")
def generate_uml(body: DiagramInput, db: Session = Depends(get_db)):
    def do_gen():
        return ai_service.generate_diagrams(body.text)

    result = audit_service.with_audit(db, "generate_uml", {"text_length": len(body.text)}, do_gen)

    import uuid
    fake_id = str(uuid.uuid4())
    doc = DocumentModel(id=fake_id, title="UML Generation", text=body.text, doc_type="tz")
    db.add(doc)
    db.flush()

    return _build_diagram_set(fake_id, result, db)


@router.post("/diagrams/generate-erd")
def generate_erd(body: DiagramInput, db: Session = Depends(get_db)):
    def do_gen():
        return ai_service.generate_diagrams(body.text)

    result = audit_service.with_audit(db, "generate_erd", {"text_length": len(body.text)}, do_gen)

    import uuid
    fake_id = str(uuid.uuid4())
    doc = DocumentModel(id=fake_id, title="ERD Generation", text=body.text, doc_type="tz")
    db.add(doc)
    db.flush()

    return _build_diagram_set(fake_id, result, db)
