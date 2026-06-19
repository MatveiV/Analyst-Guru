import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


def new_uuid():
    return str(uuid.uuid4())


def now():
    return datetime.utcnow()


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    title = Column(String(500), nullable=False)
    text = Column(Text, nullable=False)
    doc_type = Column(String(50), default="tz", nullable=False)
    project_name = Column(String(255), nullable=True)
    is_kb = Column(Boolean, default=False, nullable=False)

    snippets = relationship("Snippet", back_populates="document", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="document", cascade="all, delete-orphan")
    architecture_reviews = relationship("ArchitectureReview", back_populates="document", cascade="all, delete-orphan")
    api_specs = relationship("APISpec", back_populates="document", cascade="all, delete-orphan")
    adr_records = relationship("ADRRecord", back_populates="document", cascade="all, delete-orphan")
    diagram_artifacts = relationship("DiagramArtifact", back_populates="document", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDoc", back_populates="document", cascade="all, delete-orphan")


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    snippet_text = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)

    document = relationship("Document", back_populates="snippets")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    review_json = Column(Text, nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)
    confidence = Column(String(10), default="low", nullable=False)
    error = Column(String(100), nullable=True)

    document = relationship("Document", back_populates="reviews")


class QARun(Base):
    __tablename__ = "qa_runs"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources_json = Column(Text, default="[]", nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)
    error = Column(String(100), nullable=True)


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    action = Column(String(100), nullable=False)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    status = Column(String(20), default="ok", nullable=False)
    error = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0, nullable=False)


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    memory_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text, default="[]", nullable=False)
    project_name = Column(String(255), nullable=True)
    relevance_score = Column(Float, nullable=True)


class ArchitectureReview(Base):
    __tablename__ = "architecture_reviews"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    recommendation_json = Column(Text, nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)

    document = relationship("Document", back_populates="architecture_reviews")


class APISpec(Base):
    __tablename__ = "api_specs"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    openapi_json = Column(Text, nullable=True)
    openapi_yaml = Column(Text, nullable=True)

    document = relationship("Document", back_populates="api_specs")


class ADRRecord(Base):
    __tablename__ = "adr_records"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    adr_json = Column(Text, nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)
    confidence = Column(String(10), default="low", nullable=False)

    document = relationship("Document", back_populates="adr_records")


class DiagramArtifact(Base):
    __tablename__ = "diagram_artifacts"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    diagram_type = Column(String(50), nullable=False)
    notation = Column(String(20), nullable=False)
    source_code = Column(Text, nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)

    document = relationship("Document", back_populates="diagram_artifacts")


class AiSetting(Base):
    __tablename__ = "ai_settings"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    updated_at = Column(DateTime, default=now, onupdate=now, nullable=False)
    provider = Column(String(20), default="openrouter", nullable=False)
    api_key = Column(Text, nullable=True)
    base_url = Column(Text, nullable=True)
    model = Column(String(100), nullable=True)
    max_tokens = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)


class RiskCatalogItem(Base):
    __tablename__ = "risk_catalog"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    severity = Column(String(10), default="medium", nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    mitigation = Column(Text, nullable=False)
    project_context = Column(String(255), nullable=True)


class ProjectLesson(Base):
    __tablename__ = "project_lessons"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    project_name = Column(String(255), nullable=False)
    lesson = Column(Text, nullable=False)
    impact = Column(Text, nullable=False)
    tags = Column(Text, default="[]", nullable=False)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    context = Column(Text, nullable=False)
    problem = Column(Text, nullable=False)
    decision = Column(Text, nullable=False)
    alternatives = Column(Text, default="[]", nullable=False)
    consequences = Column(Text, default="{}", nullable=False)
    status = Column(String(20), default="proposed", nullable=False)

    document = relationship("Document", backref="decisions")


class GeneratedDoc(Base):
    __tablename__ = "generated_docs"

    id = Column(String, primary_key=True, default=new_uuid)
    created_at = Column(DateTime, default=now, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    content_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    needs_review = Column(Boolean, default=False, nullable=False)
    confidence = Column(String(10), default="low", nullable=False)

    document = relationship("Document", back_populates="generated_documents")
