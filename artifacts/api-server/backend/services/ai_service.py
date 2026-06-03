import os
import json
import time
import logging
from typing import Any, Optional
from pydantic import BaseModel, Field
from pydantic import ValidationError

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import AiSetting

logger = logging.getLogger(__name__)


class ReviewOutput(BaseModel):
    summary: str = Field(min_length=5)
    risks: list[dict] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    questions_to_client: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    similar_projects: list[str] = Field(default_factory=list)
    lessons_learned: list[str] = Field(default_factory=list)
    related_decisions: list[str] = Field(default_factory=list)
    architecture_risks: list[str] = Field(default_factory=list)
    confidence: str = Field(default="low")
    needs_review: bool = Field(default=True)


class AnswerOutput(BaseModel):
    answer: str = Field(min_length=1)
    sources: list[dict] = Field(default_factory=list)
    confidence: str = Field(default="low")
    needs_review: bool = Field(default=True)


class ArchitectureOutput(BaseModel):
    recommended_pattern: str = Field(min_length=1)
    rationale: str = Field(default="")
    alternatives: list[dict] = Field(default_factory=list)
    integration_recommendations: list[str] = Field(default_factory=list)
    risks: list[dict] = Field(default_factory=list)
    confidence: str = Field(default="low")
    needs_review: bool = Field(default=True)


class ADROutput(BaseModel):
    title: str = Field(min_length=1)
    status: str = Field(default="proposed")
    context: str = Field(default="")
    problem: str = Field(default="")
    decision: str = Field(default="")
    alternatives: list[dict] = Field(default_factory=list)
    consequences: dict = Field(default_factory=lambda: {"positive": [], "negative": []})
    confidence: str = Field(default="low")
    needs_review: bool = Field(default=True)


class DocGenOutput(BaseModel):
    content: str = Field(min_length=1)
    confidence: str = Field(default="medium")
    needs_review: bool = Field(default=False)


class OpenAPIOutput(BaseModel):
    openapi_yaml: str = Field(default="")
    openapi_json: str = Field(default="")
    confidence: str = Field(default="low")
    needs_review: bool = Field(default=True)


class DiagramOutput(BaseModel):
    c4_context: str = Field(default="")
    c4_container: str = Field(default="")
    c4_component: str = Field(default="")
    use_case: str = Field(default="")
    sequence: str = Field(default="")
    class_diagram: str = Field(default="")
    erd: str = Field(default="")
    mermaid_flowchart: str = Field(default="")
    confidence: str = Field(default="low")
    needs_review: bool = Field(default=True)

LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))

PROXYAPI_BASE_URL = os.environ.get("PROXYAPI_BASE_URL", "https://api.proxyapi.ru/openai/v1")


def _load_ai_settings() -> tuple[str, str, str, str]:
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    proxyapi_key = os.environ.get("PROXYAPI_API_KEY", "")
    try:
        db: Session = SessionLocal()
        setting = db.query(AiSetting).first()
        if setting and setting.api_key:
            if setting.provider == "anthropic":
                anthropic_key = setting.api_key
            elif setting.provider == "openai":
                openai_key = setting.api_key
            elif setting.provider == "proxyapi":
                proxyapi_key = setting.api_key
            provider = setting.provider
        db.close()
    except Exception:
        logger.warning("Could not load AI settings from DB, using env defaults")
    return provider, anthropic_key, openai_key, proxyapi_key

REVIEW_SCHEMA = """{
  "summary": "string (2-6 sentences about the document and what needs to be built)",
  "risks": [{"severity": "low|medium|high", "description": "string"}],
  "missing_requirements": ["string"],
  "questions_to_client": ["string"],
  "acceptance_criteria": ["string"],
  "similar_projects": ["string"],
  "lessons_learned": ["string"],
  "related_decisions": ["string"],
  "architecture_risks": ["string"],
  "confidence": "high|medium|low",
  "needs_review": false
}"""

ANSWER_SCHEMA = '{"answer": "string", "sources": [{"quote": "string"}], "confidence": "high|medium|low", "needs_review": false}'

ARCH_SCHEMA = """{
  "recommended_pattern": "Monolith|Modular Monolith|Microservices|Event-Driven|CQRS",
  "rationale": "string",
  "alternatives": [{"pattern": "string", "pros": ["string"], "cons": ["string"]}],
  "integration_recommendations": ["string"],
  "risks": [{"severity": "low|medium|high", "description": "string"}],
  "confidence": "high|medium|low",
  "needs_review": false
}"""

ADR_SCHEMA = """{
  "title": "string",
  "status": "proposed|accepted|deprecated|superseded",
  "context": "string",
  "problem": "string",
  "decision": "string",
  "alternatives": [{"option": "string", "reason_rejected": "string"}],
  "consequences": {"positive": ["string"], "negative": ["string"]},
  "confidence": "high|medium|low",
  "needs_review": false
}"""

DIAGRAM_SCHEMA = """{
  "c4_context": "string (PlantUML code)",
  "c4_container": "string (PlantUML code)",
  "c4_component": "string (PlantUML code)",
  "use_case": "string (PlantUML code)",
  "sequence": "string (PlantUML code)",
  "class_diagram": "string (PlantUML code)",
  "erd": "string (PlantUML code)",
  "mermaid_flowchart": "string (Mermaid code)",
  "confidence": "high|medium|low",
  "needs_review": false
}"""


def _call_anthropic(system_prompt: str, user_message: str, api_key: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        raise


def _call_openai(system_prompt: str, user_message: str, api_key: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def _call_proxyapi(system_prompt: str, user_message: str, api_key: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=PROXYAPI_BASE_URL)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"ProxyAPI error: {e}")
        raise


def call_llm(system_prompt: str, user_message: str) -> str:
    provider, anthropic_key, openai_key, proxyapi_key = _load_ai_settings()

    if provider == "proxyapi" and proxyapi_key:
        return _call_proxyapi(system_prompt, user_message, proxyapi_key)
    if provider == "openai" and openai_key:
        return _call_openai(system_prompt, user_message, openai_key)
    if provider == "anthropic" and anthropic_key:
        return _call_anthropic(system_prompt, user_message, anthropic_key)

    if anthropic_key:
        return _call_anthropic(system_prompt, user_message, anthropic_key)
    if openai_key:
        return _call_openai(system_prompt, user_message, openai_key)
    if proxyapi_key:
        return _call_proxyapi(system_prompt, user_message, proxyapi_key)

    raise RuntimeError("No LLM API key configured. Set API key in Settings or via environment variables.")


def safe_parse_json(raw: str) -> Optional[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return None


def safe_fallback_review(error: str = "INVALID_JSON") -> dict:
    return {
        "summary": "Не удалось автоматически проанализировать документ. Требуется ручная проверка.",
        "risks": [{"severity": "high", "description": "Документ не прошёл автоматический анализ"}],
        "missing_requirements": ["Не удалось извлечь из-за ошибки формата"],
        "questions_to_client": [
            "Пожалуйста, уточните требования у заказчика",
            "Проверьте полноту и корректность документа",
            "Убедитесь, что документ содержит достаточно информации для анализа"
        ],
        "acceptance_criteria": [],
        "similar_projects": [],
        "lessons_learned": [],
        "related_decisions": [],
        "architecture_risks": [],
        "confidence": "low",
        "needs_review": True,
        "error": error,
    }


def safe_fallback_answer(error: str = "NO_SOURCES_FOUND") -> dict:
    return {
        "answer": "Данных недостаточно для ответа на этот вопрос. Проверьте базу знаний.",
        "sources": [],
        "confidence": "low",
        "needs_review": True,
        "error": error,
    }


def review_document(
    document_text: str,
    memory_risks: str = "",
    memory_lessons: str = "",
    memory_decisions: str = "",
) -> dict:
    system_prompt = """Ты — Senior System Analyst с 15 годами опыта. Твоя задача — провести экспертную рецензию технического задания.

ПРАВИЛА:
1. Никогда не выдумывай факты, которых нет в документе.
2. Если документ слишком короткий (менее 3 строк) или противоречивый — ставь confidence="low" и needs_review=true.
3. Вопросы заказчику должны снимать реальную неопределённость (минимум 3 если needs_review=true).
4. Критерии приёмки должны быть проверяемыми (минимум 5 если данных достаточно).
5. Риски — минимум 3 если данных достаточно.
6. Всегда возвращай строгий JSON без Markdown-обёртки."""

    user_message = f"""ДОКУМЕНТ ДЛЯ РЕЦЕНЗИИ:
{document_text}

КОНТЕКСТ ИЗ ПАМЯТИ (если есть):
Известные риски: {memory_risks or 'нет данных'}
Уроки проектов: {memory_lessons or 'нет данных'}
Связанные решения: {memory_decisions or 'нет данных'}

Верни строгий JSON:
{REVIEW_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return safe_fallback_review("INVALID_JSON")

    try:
        validated = ReviewOutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return safe_fallback_review("INVALID_JSON")

    # Apply rules: short/vague document
    text_stripped = document_text.strip()
    word_count = len(text_stripped.split())
    if len(text_stripped) < 50 or word_count < 10:
        data["confidence"] = "low"
        data["needs_review"] = True
        data["error"] = "TOO_VAGUE_INPUT"

    # Detect contradictions
    contradictions = [
        ("авторизация", "без авторизации"),
        ("oauth", "открытый доступ"),
        ("завтра", "2 месяц"),
        ("мгновенн", "одобрение менеджер"),
        ("24/7", "постоянный оператор"),
        ("не храним", "полная история"),
    ]
    text_lower = text_stripped.lower()
    for a, b in contradictions:
        if a in text_lower and b in text_lower:
            data["confidence"] = "low"
            data["needs_review"] = True
            data["error"] = "CONTRADICTORY_INPUT"
            if "risks" in data and isinstance(data["risks"], list):
                data["risks"].append({
                    "severity": "high",
                    "description": f"Обнаружено противоречие: '{a}' и '{b}'"
                })

    if data.get("error") is None and data.get("confidence") == "low":
        data["error"] = "LOW_CONFIDENCE"

    if data.get("confidence") == "low":
        data["needs_review"] = True

    return data


def answer_with_sources(question: str, context: str) -> dict:
    system_prompt = """Ты — корпоративный ассистент. Отвечай ТОЛЬКО на основе предоставленного контекста.
Если в контексте нет ответа — честно скажи "Данных недостаточно" и поставь needs_review=true.
Никогда не придумывай информацию."""

    user_message = f"""ВОПРОС: {question}

КОНТЕКСТ (фрагменты из базы знаний):
{context}

Верни строгий JSON:
{ANSWER_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return safe_fallback_answer("INVALID_JSON")

    try:
        validated = AnswerOutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return safe_fallback_answer("INVALID_JSON")

    if not data.get("sources"):
        data["needs_review"] = True
        data["error"] = "NO_SOURCES_FOUND"
        if not data.get("answer") or "недостаточно" not in data.get("answer", "").lower():
            data["answer"] = "Данных недостаточно для ответа на этот вопрос."

    if data.get("error") is None and data.get("confidence") == "low":
        data["error"] = "LOW_CONFIDENCE"

    return data


def recommend_architecture(document_text: str) -> dict:
    system_prompt = """Ты — Solution Architect. Проанализируй требования и порекомендуй архитектурный паттерн.

Учитывай:
- Масштаб системы (нагрузка, команда, сложность)
- Зрелость команды
- Временные ограничения
- NFR (нефункциональные требования)

Всегда возвращай строгий JSON без Markdown-обёртки."""

    user_message = f"""Документ: {document_text}

Верни строгий JSON:
{ARCH_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return {
            "recommended_pattern": "Monolith",
            "rationale": "Не удалось автоматически проанализировать документ.",
            "alternatives": [],
            "integration_recommendations": [],
            "risks": [{"severity": "high", "description": "Требуется ручная проверка"}],
            "confidence": "low",
            "needs_review": True
        }

    try:
        validated = ArchitectureOutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return {
            "recommended_pattern": "Monolith",
            "rationale": "Не удалось автоматически проанализировать документ.",
            "alternatives": [],
            "integration_recommendations": [],
            "risks": [{"severity": "high", "description": "Требуется ручная проверка"}],
            "confidence": "low",
            "needs_review": True
        }

    for field in ["alternatives", "integration_recommendations", "risks"]:
        if field not in data:
            data[field] = []
    return data


def generate_adr(document_text: str) -> dict:
    system_prompt = """Ты — Lead Architect. Сформулируй Architecture Decision Record (ADR) на основе документа.
Всегда возвращай строгий JSON без Markdown-обёртки."""

    user_message = f"""Документ: {document_text}

Верни строгий JSON:
{ADR_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return {
            "title": "Архитектурное решение (требует уточнения)",
            "status": "proposed",
            "context": "Не удалось автоматически сформулировать.",
            "problem": "Требуется ручная проверка.",
            "decision": "Требуется ручная проверка.",
            "alternatives": [],
            "consequences": {"positive": [], "negative": []},
            "confidence": "low",
            "needs_review": True
        }

    try:
        validated = ADROutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return {
            "title": "Архитектурное решение (требует уточнения)",
            "status": "proposed",
            "context": "Не удалось автоматически сформулировать.",
            "problem": "Требуется ручная проверка.",
            "decision": "Требуется ручная проверка.",
            "alternatives": [],
            "consequences": {"positive": [], "negative": []},
            "confidence": "low",
            "needs_review": True
        }

    if "alternatives" not in data:
        data["alternatives"] = []
    if "consequences" not in data:
        data["consequences"] = {"positive": [], "negative": []}
    return data


def generate_urs(document_text: str) -> dict:
    system_prompt = """Ты — Senior System Analyst. Составь User Requirements Specification (URS) на основе документа.
Включи: введение, область применения, пользователей, функциональные и нефункциональные требования, ограничения.
Верни JSON: {"content": "markdown text", "confidence": "high|medium|low", "needs_review": false}"""

    user_message = f"Документ: {document_text}"
    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return {"content": raw, "confidence": "medium", "needs_review": False}
    try:
        validated = DocGenOutput(**data)
        return validated.model_dump()
    except ValidationError:
        return {"content": raw, "confidence": "medium", "needs_review": False}


def generate_srs(document_text: str) -> dict:
    system_prompt = """Ты — Senior System Analyst. Составь Software Requirements Specification (SRS) по стандарту IEEE 830 на основе документа.
Включи: общее описание, функциональные требования, нефункциональные требования, интерфейсы, ограничения.
Верни JSON: {"content": "markdown text", "confidence": "high|medium|low", "needs_review": false}"""

    user_message = f"Документ: {document_text}"
    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return {"content": raw, "confidence": "medium", "needs_review": False}
    try:
        validated = DocGenOutput(**data)
        return validated.model_dump()
    except ValidationError:
        return {"content": raw, "confidence": "medium", "needs_review": False}


def generate_openapi(document_text: str) -> dict:
    system_prompt = """Ты — API Architect. Разработай OpenAPI 3.1 спецификацию на основе документа.
Верни JSON: {"openapi_yaml": "yaml string", "openapi_json": "json string", "confidence": "high|medium|low", "needs_review": false}
Сделай полную, рабочую спецификацию с paths, components, schemas."""

    user_message = f"Документ: {document_text}"
    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        fallback_yaml = f"""openapi: 3.1.0
info:
  title: Generated API
  version: 1.0.0
paths: {{}}"""
        return {"openapi_yaml": fallback_yaml, "openapi_json": "{}", "confidence": "low", "needs_review": True}
    try:
        validated = OpenAPIOutput(**data)
        return validated.model_dump()
    except ValidationError:
        fallback_yaml = f"""openapi: 3.1.0
info:
  title: Generated API
  version: 1.0.0
paths: {{}}"""
        return {"openapi_yaml": fallback_yaml, "openapi_json": "{}", "confidence": "low", "needs_review": True}


def generate_diagrams(document_text: str) -> dict:
    system_prompt = """Ты — Solution Architect. Сгенерируй диаграммы на основе документа.

ПРАВИЛА для PlantUML:
- Начинай с @startuml, заканчивай @enduml
- Для C4: используй !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
- Для Mermaid: используй синтаксис graph TD для flowchart
- Код должен быть валидным
- Если невозможно сгенерировать — верни пустую строку

Всегда возвращай строгий JSON без Markdown-обёртки."""

    user_message = f"""Документ: {document_text}

Верни строгий JSON:
{DIAGRAM_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return {
            "c4_context": "", "c4_container": "", "c4_component": "",
            "use_case": "", "sequence": "", "class_diagram": "",
            "erd": "", "mermaid_flowchart": "",
            "confidence": "low", "needs_review": True
        }

    try:
        validated = DiagramOutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return {
            "c4_context": "", "c4_container": "", "c4_component": "",
            "use_case": "", "sequence": "", "class_diagram": "",
            "erd": "", "mermaid_flowchart": "",
            "confidence": "low", "needs_review": True
        }

    for field in ["c4_context", "c4_container", "c4_component", "use_case",
                  "sequence", "class_diagram", "erd", "mermaid_flowchart"]:
        if field not in data:
            data[field] = ""

    # Validate diagrams
    plantuml_fields = ["c4_context", "c4_container", "c4_component", "use_case",
                       "sequence", "class_diagram", "erd"]
    for field in plantuml_fields:
        if data[field] and "@startuml" not in data[field]:
            data[field] = ""
            data["needs_review"] = True

    return data
