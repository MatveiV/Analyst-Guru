import os
import json
import time
import logging
from dataclasses import dataclass
from typing import Any, Optional
from pydantic import BaseModel, Field
from pydantic import ValidationError

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import AiSetting

logger = logging.getLogger(__name__)

PROVIDER_DEFAULTS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openrouter/free",
    },
    "anthropic": {
        "base_url": None,
        "model": "claude-3-5-sonnet-20241022",
    },
    "openai": {
        "base_url": None,
        "model": "gpt-4o",
    },
    "proxyapi": {
        "base_url": "https://api.proxyapi.ru/openai/v1",
        "model": "gpt-4o-mini",
    },
}


@dataclass
class AISettings:
    provider: str
    api_key: str
    base_url: str | None
    model: str
    max_tokens: int
    temperature: float


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


def _load_ai_settings() -> AISettings:
    provider = os.environ.get("LLM_PROVIDER", "openrouter").lower()
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    proxyapi_key = os.environ.get("PROXYAPI_API_KEY", "")
    base_url = None
    model = None
    max_tokens = None
    temperature = None

    try:
        db: Session = SessionLocal()
        setting = db.query(AiSetting).first()
        if setting and setting.api_key:
            if setting.provider == "openrouter":
                openrouter_key = setting.api_key
            elif setting.provider == "anthropic":
                anthropic_key = setting.api_key
            elif setting.provider == "openai":
                openai_key = setting.api_key
            elif setting.provider == "proxyapi":
                proxyapi_key = setting.api_key
            provider = setting.provider
            base_url = setting.base_url
            model = setting.model
            max_tokens = setting.max_tokens
            temperature = setting.temperature
        db.close()
    except Exception:
        logger.warning("Could not load AI settings from DB, using env defaults")

    key_map = {
        "openrouter": openrouter_key,
        "anthropic": anthropic_key,
        "openai": openai_key,
        "proxyapi": proxyapi_key,
    }
    api_key = key_map.get(provider, "")

    if not api_key:
        for p in ["openrouter", "anthropic", "openai", "proxyapi"]:
            if key_map.get(p):
                provider = p
                api_key = key_map[p]
                break

    defaults = PROVIDER_DEFAULTS.get(provider, {})
    resolved_base_url = base_url or defaults.get("base_url")
    resolved_model = model or defaults.get("model", "gpt-4o-mini")
    resolved_max_tokens = max_tokens or LLM_MAX_TOKENS
    resolved_temperature = temperature if temperature is not None else LLM_TEMPERATURE

    return AISettings(
        provider=provider,
        api_key=api_key,
        base_url=resolved_base_url,
        model=resolved_model,
        max_tokens=resolved_max_tokens,
        temperature=resolved_temperature,
    )

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


REASONING_PROMPTS = {
    "cot": """
ВАЖНО: Используй Chain-of-Thought (цепочку рассуждений).
Перед ответом:
1. Проанализируй требования документа
2. Выяви ключевые элементы, риски и неопределённости
3. Сформулируй выводы на основе анализа

Помести свои рассуждения в тег <reasoning>...</reasoning>, затем верни JSON.""",
    "react": """
ВАЖНО: Используй ReAct (рассуждение + проверка).
1. Thought: Проанализируй задачу — что от тебя требуется, какие данные есть
2. Action: Определи, какие проверки нужно выполнить (полнота, противоречия, риски)
3. Observation: Проанализируй результат проверок, зафиксируй выводы
4. Answer: Сформулируй окончательный ответ на основе наблюдений
5. Verify: Перепроверь ответ — все ли требования учтены, нет ли пропусков

Помести свои рассуждения в тег <reasoning>...</reasoning>, затем верни JSON.""",
}


def _build_prompt(base: str, reasoning_mode: str) -> str:
    if reasoning_mode in REASONING_PROMPTS:
        return base + REASONING_PROMPTS[reasoning_mode]
    return base


def _extract_reasoning(raw: str) -> tuple[str, str]:
    """Extract <reasoning>...</reasoning> block from LLM output.
    Returns (cleaned_text, reasoning_text)."""
    import re
    m = re.search(r'<reasoning>(.*?)</reasoning>', raw, re.DOTALL)
    if m:
        cleaned = raw[:m.start()] + raw[m.end():]
        return cleaned.strip(), m.group(1).strip()
    return raw.strip(), ""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.api_key)
        message = client.messages.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        raise


def _call_openai(settings: AISettings, system_prompt: str, user_message: str) -> str:
    try:
        from openai import OpenAI
        kwargs = {}
        if settings.base_url:
            kwargs["base_url"] = settings.base_url
        client = OpenAI(api_key=settings.api_key, **kwargs)
        response = client.chat.completions.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


def _call_proxyapi(settings: AISettings, system_prompt: str, user_message: str) -> str:
    try:
        from openai import OpenAI
        base = settings.base_url or "https://api.proxyapi.ru/openai/v1"
        client = OpenAI(api_key=settings.api_key, base_url=base)
        response = client.chat.completions.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"ProxyAPI error: {e}")
        raise


def _call_openrouter(settings: AISettings, system_prompt: str, user_message: str) -> str:
    try:
        from openai import OpenAI
        base = settings.base_url or "https://openrouter.ai/api/v1"
        client = OpenAI(api_key=settings.api_key, base_url=base)
        response = client.chat.completions.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        raise


def call_llm(system_prompt: str, user_message: str) -> str:
    settings = _load_ai_settings()

    if not settings.api_key:
        raise RuntimeError("No LLM API key configured. Set API key in Settings or via environment variables.")

    router = {
        "openrouter": _call_openrouter,
        "anthropic": _call_anthropic,
        "openai": _call_openai,
        "proxyapi": _call_proxyapi,
    }

    func = router.get(settings.provider)
    if func:
        return func(settings, system_prompt, user_message)

    raise RuntimeError(f"Unknown provider: {settings.provider}")


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
    reasoning_mode: str = "none",
) -> dict:
    base_prompt = """Ты — Senior System Analyst с 15 годами опыта. Твоя задача — провести экспертную рецензию технического задания (ТЗ) на соответствие ГОСТ 34 и ГОСТ 19.

НОРМАТИВНЫЕ ТРЕБОВАНИЯ:
- ГОСТ 34.602-89 — состав и содержание ТЗ на создание автоматизированной системы: общие сведения, назначение и цели создания, характеристика объекта, требования к системе, состав и содержание работ, порядок контроля и приёмки.
- ГОСТ 19.201-78 — техническое задание на программное изделие: введение, основания для разработки, назначение, требования к программе, требования к программной документации, стадии и этапы разработки, порядок контроля и приёмки.

ПРАВИЛА:
1. Никогда не выдумывай факты, которых нет в документе.
2. Если документ слишком короткий (менее 3 строк) или противоречивый — ставь confidence="low" и needs_review=true.
3. Вопросы заказчику должны снимать реальную неопределённость (минимум 3 если needs_review=true).
4. Критерии приёмки должны быть проверяемыми (минимум 5 если данных достаточно).
5. Риски — минимум 3 если данных достаточно.
6. При оценке полноты ТЗ учитывай наличие разделов по ГОСТ 34 и ГОСТ 19. Отмечай отсутствующие обязательные разделы.
7. Всегда возвращай строгий JSON без Markdown-обёртки."""

    system_prompt = _build_prompt(base_prompt, reasoning_mode)

    user_message = f"""ДОКУМЕНТ ДЛЯ РЕЦЕНЗИИ:
{document_text}

КОНТЕКСТ ИЗ ПАМЯТИ (если есть):
Известные риски: {memory_risks or 'нет данных'}
Уроки проектов: {memory_lessons or 'нет данных'}
Связанные решения: {memory_decisions or 'нет данных'}

Верни строгий JSON:
{REVIEW_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    reasoning = ""
    if reasoning_mode != "none":
        raw, reasoning = _extract_reasoning(raw)
    data = safe_parse_json(raw)
    if data is None:
        return safe_fallback_review("INVALID_JSON")

    try:
        validated = ReviewOutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return safe_fallback_review("INVALID_JSON")

    if reasoning:
        data["reasoning"] = reasoning

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


def answer_with_sources(question: str, context: str, reasoning_mode: str = "none") -> dict:
    base_prompt = """Ты — корпоративный ассистент. Отвечай ТОЛЬКО на основе предоставленного контекста.
Если в контексте нет ответа — честно скажи "Данных недостаточно" и поставь needs_review=true.
Никогда не придумывай информацию."""

    system_prompt = _build_prompt(base_prompt, reasoning_mode)

    user_message = f"""ВОПРОС: {question}

КОНТЕКСТ (фрагменты из базы знаний):
{context}

Верни строгий JSON:
{ANSWER_SCHEMA}"""

    raw = call_llm(system_prompt, user_message)
    reasoning = ""
    if reasoning_mode != "none":
        raw, reasoning = _extract_reasoning(raw)
    data = safe_parse_json(raw)
    if data is None:
        return safe_fallback_answer("INVALID_JSON")

    try:
        validated = AnswerOutput(**data)
        data = validated.model_dump()
    except ValidationError:
        return safe_fallback_answer("INVALID_JSON")

    if reasoning:
        data["reasoning"] = reasoning

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
    system_prompt = """Ты — Senior System Analyst. Составь User Requirements Specification (URS) по стандарту GAMP 5 на основе документа.

Структура URS (GAMP 5):
1. **Введение и Цель (Introduction)** — зачем система разрабатывается, какие бизнес-задачи решает.
2. **Область применения (Scope)** — где будет использоваться система, кто конечные пользователи, границы системы.
3. **Описание процессов (System Description)** — бизнес-процессы, которые должна поддерживать система, описание рабочих потоков.
4. **Пользовательские требования (User Requirements)** — функциональные ожидания пользователей (что система должна делать) и нефункциональные (производительность, безопасность, соответствие регуляторике). Каждое требование должно быть проверяемым.
5. **Ограничения (Constraints)** — окружение, совместимость с текущей инфраструктурой, нормативные требования, бюджет, сроки.
6. **Критерии приемки (Acceptance Criteria)** — как пользователь будет проверять, что система работает корректно. Должны быть измеримыми и объективными.

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
    system_prompt = """Ты — Senior System Analyst. Составь Software Requirements Specification (SRS) по стандарту ISO/IEC/IEEE 29148 на основе документа.

Структура SRS (ISO/IEC/IEEE 29148):
1. **Введение (Introduction)** — цель документа, аудитория, обзор системы, ссылки на URS и смежные документы.
2. **Общее описание (General Description)** — перспектива продукта (автономен или часть системы), основные функции, классы пользователей, операционная среда, ограничения и допущения.
3. **Требования к внешним интерфейсам (External Interface Requirements)** — пользовательский интерфейс (UI/UX), аппаратные интерфейсы, программные интерфейсы (API), требования к сетям и протоколам.
4. **Функциональные требования (Functional Requirements)** — детальное описание каждой функции с уникальными идентификаторами (FR-001, FR-002, ...), входные/выходные данные, алгоритмы обработки, исключительные ситуации и обработка ошибок.
5. **Нефункциональные требования (Non-Functional Requirements)** — производительность (время отклика, пропускная способность), безопасность (аутентификация, авторизация, шифрование), доступность (uptime, SLA), масштабируемость, надёжность (RTO, RPO), стандарты качества.
6. **Требования к данным (Data Requirements)** — хранение данных, резервное копирование, архивация, сроки хранения, импорт/экспорт.

Все требования должны быть: однозначными, проверяемыми, атомарными и прослеживаемыми.

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
