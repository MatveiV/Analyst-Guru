import os
import json
import time
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))

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


def _call_anthropic(system_prompt: str, user_message: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
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


def _call_openai(system_prompt: str, user_message: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
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


def call_llm(system_prompt: str, user_message: str) -> str:
    if not ANTHROPIC_API_KEY and not OPENAI_API_KEY:
        raise RuntimeError("No LLM API key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return _call_openai(system_prompt, user_message)
    if ANTHROPIC_API_KEY:
        return _call_anthropic(system_prompt, user_message)
    return _call_openai(system_prompt, user_message)


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
        "needs_review": True
    }


def safe_fallback_answer(error: str = "NO_SOURCES_FOUND") -> dict:
    return {
        "answer": "Данных недостаточно для ответа на этот вопрос. Проверьте базу знаний.",
        "sources": [],
        "confidence": "low",
        "needs_review": True
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

    # Validate required fields
    required = ["summary", "confidence", "needs_review"]
    if not all(k in data for k in required):
        return safe_fallback_review("INVALID_JSON")

    # Apply rules: short/vague document
    text_stripped = document_text.strip()
    if len(text_stripped) < 50 or len(text_stripped.split()) < 10:
        data["confidence"] = "low"
        data["needs_review"] = True

    if data.get("confidence") == "low":
        data["needs_review"] = True

    # Ensure arrays exist
    for field in ["risks", "missing_requirements", "questions_to_client", "acceptance_criteria",
                  "similar_projects", "lessons_learned", "related_decisions", "architecture_risks"]:
        if field not in data:
            data[field] = []

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

    if not data.get("sources"):
        data["needs_review"] = True
        if not data.get("answer") or "недостаточно" not in data.get("answer", "").lower():
            data["answer"] = "Данных недостаточно для ответа на этот вопрос."

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
    return data


def generate_srs(document_text: str) -> dict:
    system_prompt = """Ты — Senior System Analyst. Составь Software Requirements Specification (SRS) по стандарту IEEE 830 на основе документа.
Включи: общее описание, функциональные требования, нефункциональные требования, интерфейсы, ограничения.
Верни JSON: {"content": "markdown text", "confidence": "high|medium|low", "needs_review": false}"""

    user_message = f"Документ: {document_text}"
    raw = call_llm(system_prompt, user_message)
    data = safe_parse_json(raw)
    if data is None:
        return {"content": raw, "confidence": "medium", "needs_review": False}
    return data


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
    return data


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
