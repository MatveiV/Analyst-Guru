# MASTER PROMPT: AnalystGuru — AI System Analyst Copilot

> **Роль:** Ты — Senior Solution Architect, Lead System Analyst, Lead Python Developer, AI Architect и Technical Product Owner.
>
> **Задача:** Спроектируй и реализуй полноценное production-ready веб-приложение **AnalystGuru** — AI System Analyst Copilot with Team Memory, RAG, ADR & Diagram Generation, API Design and Architecture Recommendation Engine.

---

## 0. КОНТЕКСТ И БИЗНЕС-ЦЕЛЬ

Организации системно теряют накопленные знания по проектам. Системные аналитики повторяют одни и те же вопросы. Архитектурные решения забываются. Требования дублируются. Риски «открываются заново».

**AnalystGuru** решает эту проблему, объединяя в одном продукте:

| Проблема | Решение в системе |
|---|---|
| «Сырые» ТЗ уходят в разработку без анализа | AI-рецензент документов (Вариант №2) |
| Знания команды хранятся «в головах» | Система знаний с RAG и источниками (Вариант №5) |
| Архитектурные решения не фиксируются | ADR Generator + Architecture Recommendation Engine |
| Диаграммы рисуются вручную | Diagram Generation Engine (PlantUML + Mermaid) |
| Нет единого аудита операций | audit_runs для каждого действия |

**Целевая аудитория продукта:** Senior System Analyst, Lead System Analyst, Business Analyst, Solution Architect, AI Business Analyst, Product Analyst.

**Портфолио-цель:** Проект должен выглядеть как реальный enterprise-продукт, пригодный для демонстрации на собеседованиях уровня Senior/Lead.

---

## 1. ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ ВЫПУСКНОГО ПРОЕКТА

Система **обязана** реализовывать полный сквозной стек:

```
Веб-панель (React) → REST API (FastAPI) → База данных (SQLite/PostgreSQL)
       → LLM-операция (строгий JSON) → Контроль качества → Аудит
```

### 1.1 Критерии воспроизводимости

- Запуск по `README.md` ≤ 10 минут на чистой машине
- `Dockerfile` + `docker-compose.yml`
- `.env.example` без секретов
- 10 тестовых входов в `tests_data/`
- Демо-видео сценарии (описать в README)

### 1.2 Обязательный элемент качества — «Ручная проверка»

Система **никогда не врёт уверенно**. Когда уверенность низкая или данных недостаточно:

- Выставляет `needs_review: true`
- Сохраняет причину в `audit_runs.error` (коды: `LOW_CONFIDENCE`, `TOO_VAGUE_INPUT`, `CONTRADICTORY_INPUT`, `INVALID_JSON`, `NO_SOURCES_FOUND`)
- Показывает метку «Требует проверки» в веб-панели
- Возвращает безопасный результат **без галлюцинаций**

---

## 2. АРХИТЕКТУРА СИСТЕМЫ

### 2.1 Высокоуровневая схема (C4 Level 1 — System Context)

```
[Аналитик] → [AnalystGuru Web UI (React)]
                      ↓
              [FastAPI Backend]
               ↙      ↓      ↘
        [SQLite/    [RAG      [Anthropic /
        PostgreSQL] Engine]   OpenAI API]
                      ↓
              [Audit Trail]
```

### 2.2 Модули системы

| Модуль | Назначение |
|---|---|
| **Document Manager** | CRUD документов / ТЗ |
| **AI Reviewer** | Рецензия ТЗ → строгий JSON |
| **Knowledge Base** | Загрузка документов команды |
| **RAG Engine** | Поиск по фрагментам + цитаты |
| **Memory Framework** | Семантическая / эпизодическая / решенческая / рисковая / требовательная память |
| **URS/SRS Generator** | Генерация требований |
| **ADR Generator** | Архитектурные решения |
| **Architecture Engine** | Рекомендации паттернов |
| **API Design Engine** | OpenAPI 3.1 спецификации |
| **Diagram Engine** | PlantUML + Mermaid диаграммы |
| **Audit Center** | Полная история всех операций |

### 2.3 Технологический стек

| Слой | Технологии |
|---|---|
| **Frontend** | React 18 + TypeScript + Tailwind CSS + React Router |
| **Backend** | Python 3.11 + FastAPI + Pydantic v2 |
| **ORM** | SQLAlchemy 2.0 + Alembic (миграции) |
| **База данных** | SQLite (dev) / PostgreSQL (prod) |
| **RAG** | LangChain + Haystack (гибридный поиск) |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **LLM** | Anthropic Claude / OpenAI GPT-4 (через `.env`) |
| **Диаграммы** | Генерация кода PlantUML + Mermaid (текст) |
| **Экспорт** | python-docx, csv, json, PyYAML |
| **Деплой** | Docker + docker-compose |
| **Тесты** | pytest + httpx |

---

## 3. БАЗА ДАННЫХ — ПОЛНАЯ СХЕМА

### 3.1 Все таблицы (SQLAlchemy models)

```python
# documents — входные документы / ТЗ
class Document:
    id: UUID (PK)
    created_at: datetime
    title: str (not null)
    text: str (not null, max 30_000 chars)
    doc_type: str  # "tz", "brd", "user_story", "srs", "kb_article"
    project_name: str | None

# snippets — фрагменты документов для RAG
class Snippet:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID (FK → documents)
    snippet_text: str
    embedding: bytes | None  # сериализованный вектор

# reviews — результаты AI-рецензий
class Review:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID (FK → documents)
    review_json: str  # полный JSON-отчёт
    needs_review: bool
    confidence: str  # "high"|"medium"|"low"
    error: str | None

# qa_runs — история вопросов к базе знаний
class QARun:
    id: UUID (PK)
    created_at: datetime
    question: str
    answer: str
    sources_json: str  # JSON-массив {document_id, quote}
    needs_review: bool
    error: str | None

# audit_runs — аудит ВСЕХ операций
class AuditRun:
    id: UUID (PK)
    created_at: datetime
    action: str       # "review", "ask", "generate_urs", "generate_adr", ...
    input: str        # JSON входных данных
    output: str       # JSON результата
    status: str       # "ok" | "error" | "needs_review"
    error: str | None
    duration_ms: int

# memory_items — фреймворк памяти
class MemoryItem:
    id: UUID (PK)
    created_at: datetime
    memory_type: str  # "semantic"|"episodic"|"decision"|"risk"|"requirement"
    content: str
    tags: str         # JSON-массив тегов
    project_name: str | None
    relevance_score: float | None

# decisions — ADR-записи
class Decision:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID | None (FK → documents)
    context: str
    problem: str
    decision: str
    alternatives: str  # JSON
    consequences: str
    status: str        # "proposed"|"accepted"|"deprecated"|"superseded"

# risks_catalog — каталог известных рисков
class RiskCatalogItem:
    id: UUID (PK)
    created_at: datetime
    severity: str     # "low"|"medium"|"high"
    category: str
    description: str
    mitigation: str
    project_context: str | None

# project_lessons — lessons learned
class ProjectLesson:
    id: UUID (PK)
    created_at: datetime
    project_name: str
    lesson: str
    impact: str
    tags: str

# architecture_reviews — рекомендации архитектуры
class ArchitectureReview:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID (FK → documents)
    recommendation_json: str  # JSON с паттерном, обоснованием, альтернативами
    needs_review: bool

# api_specs — сгенерированные API-спецификации
class APISpec:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID (FK → documents)
    openapi_json: str
    openapi_yaml: str

# adr_records — хранение ADR
class ADRRecord:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID (FK → documents)
    adr_json: str

# diagram_artifacts — сгенерированные диаграммы
class DiagramArtifact:
    id: UUID (PK)
    created_at: datetime
    document_id: UUID (FK → documents)
    diagram_type: str  # "c4_context"|"c4_container"|"c4_component"|"sequence"|"class"|"erd"|"use_case"|"activity"|"state"|"deployment"
    notation: str      # "plantuml"|"mermaid"
    source_code: str
```

### 3.2 Правила целостности данных

- При создании рецензии → полный JSON сохраняется в `review_json`
- Если LLM вернул невалидный JSON → `needs_review=true`, `error="INVALID_JSON"`, возвращается безопасный шаблон
- Если `sources_json` пустой в `qa_runs` → `needs_review=true` **обязательно**
- Каждая операция → одна запись в `audit_runs` (без исключений)

---

## 4. REST API — ПОЛНЫЙ СПИСОК ЭНДПОИНТОВ

### 4.1 Document Manager

```
POST   /documents                          # создать документ
GET    /documents                          # список документов
GET    /documents/{id}                     # получить документ
```

### 4.2 AI Reviewer (Вариант №2)

```
POST   /documents/{id}/review              # запустить рецензию → review_id
GET    /reviews                            # список рецензий
GET    /reviews/{id}                       # получить рецензию
POST   /ai/review                          # прямой вызов AI (для тестов/отладки)
```

### 4.3 Knowledge Base — Team Memory (Вариант №5)

```
POST   /kb/documents                       # добавить документ в базу знаний
GET    /kb/documents                       # список KB-документов
POST   /kb/ask                             # задать вопрос → ответ + источники
POST   /ai/answer_with_sources             # прямой вызов AI (для тестов)
```

### 4.4 Document Generators

```
POST   /documents/{id}/generate-urs        # генерация URS
POST   /documents/{id}/generate-srs        # генерация SRS
POST   /documents/{id}/generate-adr        # генерация ADR
POST   /documents/{id}/design-api          # генерация OpenAPI спецификации
POST   /documents/{id}/recommend-architecture # рекомендация архитектуры
```

### 4.5 Memory Framework

```
POST   /memory/store                       # сохранить элемент памяти
POST   /memory/search                      # семантический поиск по памяти
GET    /memory/recent                      # последние элементы памяти
POST   /memory/consolidate                 # консолидация и дедупликация памяти
```

### 4.6 Diagram Engine

```
POST   /documents/{id}/generate-diagrams   # генерировать все диаграммы → diagram_set_id
GET    /diagrams/{id}                      # получить диаграмму
POST   /diagrams/generate-c4               # C4 диаграммы
POST   /diagrams/generate-uml             # UML диаграммы
POST   /diagrams/generate-erd             # ERD диаграмма
```

### 4.7 Audit & Export

```
GET    /audit                              # история audit_runs (фильтры: action, status, date)
GET    /reviews/{id}/export/json           # экспорт рецензии в JSON
GET    /reviews/{id}/export/csv            # экспорт рецензии в CSV
GET    /documents/{id}/export/docx         # экспорт URS/SRS в DOCX
```

---

## 5. СХЕМЫ СТРОГОГО JSON (LLM OUTPUT CONTRACTS)

### 5.1 AI Review Schema (POST /ai/review)

**Вход:**
```json
{ "text": "string" }
```

**Выход (строгий, валидировать через Pydantic):**
```json
{
  "summary": "string (2–6 предложений: о чём документ и что хотят сделать)",
  "risks": [
    {
      "severity": "low|medium|high",
      "description": "string"
    }
  ],
  "missing_requirements": ["string"],
  "questions_to_client": ["string"],
  "acceptance_criteria": ["string"],
  "similar_projects": ["string"],
  "lessons_learned": ["string"],
  "related_decisions": ["string"],
  "architecture_risks": ["string"],
  "confidence": "high|medium|low",
  "needs_review": false
}
```

**Правила минимальных значений:**
- `risks` — минимум 3 элемента (если есть данные)
- `acceptance_criteria` — минимум 5 элементов (если есть данные)
- `questions_to_client` — минимум 3 (если `needs_review=true`)

**Правила `needs_review=true`:**
- `confidence="low"`
- документ менее 3 строк / без сути
- в документе обнаружены противоречия
- LLM вернул невалидный JSON (`error="INVALID_JSON"`)

### 5.2 AI Answer with Sources Schema (POST /ai/answer_with_sources)

**Вход:**
```json
{
  "question": "string",
  "context": "string"
}
```

**Выход:**
```json
{
  "answer": "string",
  "sources": [
    { "quote": "string" }
  ],
  "confidence": "high|medium|low",
  "needs_review": false
}
```

**Правило:** если `sources` пустой → `needs_review=true` и `answer` в духе «Данных недостаточно для ответа на этот вопрос.»

### 5.3 Architecture Recommendation Schema

```json
{
  "recommended_pattern": "Monolith|Modular Monolith|Microservices|Event-Driven|CQRS",
  "rationale": "string",
  "alternatives": [
    {
      "pattern": "string",
      "pros": ["string"],
      "cons": ["string"]
    }
  ],
  "integration_recommendations": ["REST|Kafka|RabbitMQ|gRPC|Webhook|File Exchange"],
  "risks": [
    { "severity": "low|medium|high", "description": "string" }
  ],
  "confidence": "high|medium|low",
  "needs_review": false
}
```

### 5.4 ADR Schema

```json
{
  "title": "string",
  "status": "proposed|accepted|deprecated|superseded",
  "context": "string",
  "problem": "string",
  "decision": "string",
  "alternatives": [
    { "option": "string", "reason_rejected": "string" }
  ],
  "consequences": {
    "positive": ["string"],
    "negative": ["string"]
  },
  "confidence": "high|medium|low",
  "needs_review": false
}
```

### 5.5 Diagram Generation Schema

```json
{
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
}
```

---

## 6. RAG ENGINE — ДЕТАЛЬНАЯ РЕАЛИЗАЦИЯ

### 6.1 Принцип работы

```
Загрузка документа → Нарезка на фрагменты (абзацы) → Хранение в snippets
         ↓
Вопрос пользователя → Keyword Search + Semantic Search (гибрид)
         ↓
Top-K релевантных фрагментов → Формирование контекста → LLM
         ↓
Ответ + Цитаты (document_id + quote) → QA Run → Audit
```

### 6.2 Стратегия нарезки

- Разбивать по двойному переносу строки (`\n\n`) — абзацы
- Минимальная длина фрагмента: 50 символов
- Максимальная длина фрагмента: 1000 символов
- Перекрытие (overlap): 100 символов между соседними чанками

### 6.3 Поиск

**Keyword search:** SQL `LIKE` или `FTS5` (SQLite Full-Text Search)

**Semantic search (если доступен):**
- Модель: `sentence-transformers/all-MiniLM-L6-v2`
- Хранить эмбеддинги в `snippets.embedding` (bytes)
- Косинусное сходство для ранжирования

**Гибридный ранкинг:** `score = 0.5 * keyword_score + 0.5 * semantic_score`

### 6.4 LangChain + Haystack интеграция

```python
# LangChain: оркестрация цепочек
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Haystack: индексирование и ретривал
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, EmbeddingRetriever
```

Если Haystack недоступен — допустим fallback на чистый LangChain + SQLite FTS5.

---

## 7. ФРЕЙМВОРК ПАМЯТИ (Memory Framework)

### 7.1 Типы памяти

| Тип | Назначение | Примеры данных |
|---|---|---|
| `semantic` | Долгосрочные знания | стандарты, архитектурные принципы, интеграционные конвенции |
| `episodic` | Опыт по проектам | инциденты, ретроспективы, истории внедрения |
| `decision` | Архитектурные решения | ADR-записи |
| `risk` | Известные риски | каталог рисков с mitigation |
| `requirement` | Исторические требования | паттерны требований по доменам |

### 7.2 API памяти

**POST /memory/store:**
```json
{
  "memory_type": "semantic|episodic|decision|risk|requirement",
  "content": "string",
  "tags": ["string"],
  "project_name": "string|null"
}
```

**POST /memory/search:**
```json
{
  "query": "string",
  "memory_type": "string|null",
  "limit": 10
}
```

### 7.3 Использование памяти в рецензии

При вызове `POST /documents/{id}/review` система **обязана**:
1. Искать в `memory_items` по типу `risk` — похожие известные риски
2. Искать по типу `decision` — связанные ADR
3. Искать по типу `episodic` — уроки из похожих проектов
4. Добавлять найденное в промпт как контекст
5. Отражать в полях `similar_projects`, `lessons_learned`, `related_decisions`

---

## 8. DIAGRAM GENERATION ENGINE

### 8.1 Поддерживаемые нотации

**PlantUML:**
- C4 Context / Container / Component
- UML: Use Case, Activity, Sequence, Class, State Machine, Deployment, Package
- ERD

**Mermaid:**
- `graph TD` (flowchart)
- `sequenceDiagram`
- `classDiagram`
- `erDiagram`

### 8.2 Промпт для генерации C4 (пример)

```
Ты — Solution Architect. На основе следующего документа сгенерируй валидный PlantUML код для C4 диаграммы.

ДОКУМЕНТ:
{document_text}

ТРЕБОВАНИЯ:
- Используй !include C4_Context.puml из официального репозитория plantuml-stdlib
- Определи всех актёров (Person) и системы (System)
- Добавь все ключевые связи (Rel)
- Код должен компилироваться без ошибок на PlantUML Server
- Возврати ТОЛЬКО PlantUML код, без пояснений

Верни строгий JSON:
{"c4_context": "<plantuml code>", "confidence": "high|medium|low", "needs_review": false}
```

### 8.3 Валидация диаграмм

Для каждой сгенерированной диаграммы проверить:
- Наличие `@startuml` / `@enduml` (PlantUML)
- Наличие ключевых ключевых слов нотации
- Если валидация провалена → `needs_review=true`, `reason="INVALID_DIAGRAM"`, записать в `audit_runs`

### 8.4 Пример C4 Container Diagram

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(analyst, "System Analyst", "Загружает ТЗ, задаёт вопросы")

System_Boundary(system, "AnalystGuru") {
  Container(web, "React UI", "React 18 + TypeScript", "Веб-панель")
  Container(api, "FastAPI", "Python 3.11", "REST API")
  ContainerDb(db, "SQLite/PostgreSQL", "SQL", "Данные, аудит, память")
  Container(rag, "RAG Engine", "LangChain + Haystack", "Поиск по фрагментам")
  Container(llm, "LLM Gateway", "Anthropic/OpenAI", "AI-операции")
}

Rel(analyst, web, "Использует", "HTTPS")
Rel(web, api, "REST", "JSON")
Rel(api, db, "Читает/Пишет", "SQL")
Rel(api, rag, "Запрашивает контекст")
Rel(rag, llm, "Промпт + контекст", "API")
Rel(api, llm, "Прямые вызовы", "API")
@enduml
```

---

## 9. ВЕБ-ПАНЕЛЬ (React Frontend)

### 9.1 Структура страниц (5 разделов)

```
/                     → Dashboard (метрики, последние операции)
/documents            → Документы (список + форма + действия)
/reviews              → Рецензии (список, фильтр, экспорт)
/reviews/:id          → Детальная рецензия (summary, risks, Q&A, критерии)
/knowledge-base       → База знаний (документы + форма вопроса + история)
/architecture-studio  → Архитектурная студия (все генераторы + диаграммы)
/audit                → Аудит-центр (все audit_runs, фильтры, ошибки)
```

### 9.2 Детальные требования к экранам

#### Раздел «Документы»
- Таблица: `title`, `doc_type`, `created_at`, действия
- Форма добавления: `title` + `text` (textarea) + `doc_type`
- Кнопки действий на документе: «Создать рецензию», «Генерировать URS», «Генерировать SRS», «Генерировать ADR», «Дизайн API», «Рекомендовать архитектуру», «Диаграммы»

#### Раздел «Рецензии»
- Список рецензий: время, документ, `confidence`, метка ⚠️ «Требует проверки»
- Фильтр по `needs_review=true`
- Детальная карточка: `summary`, риски (с бейджем severity), вопросы заказчику, критерии приёмки, уроки, ADR
- Экспорт: JSON, CSV, DOCX (минимум один формат)

#### Раздел «База знаний»
- Вкладка «Документы»: список KB-документов + форма добавления + «Открыть документ»
- Вкладка «Вопросы»: поле вопроса + кнопка «Спросить» + ответ + список источников (цитата + ссылка на документ) + метка ⚠️
- Вкладка «История»: последние 50-100 вопросов + фильтр `needs_review` + карточка Q&A

#### Раздел «Архитектурная студия»

**Подвкладки:**
- **C4**: Context / Container / Component (PlantUML код + кнопка «Копировать»)
- **UML**: Use Case / Activity / Sequence / Class / State
- **ERD**: диаграмма базы данных
- **API Design**: сгенерированная OpenAPI спецификация (JSON + YAML)
- **ADR**: список ADR-записей по документу
- **Export**: PlantUML / Mermaid / Markdown / DOCX

#### Раздел «Аудит-центр»
- Таблица всех `audit_runs`: `created_at`, `action`, `status`, `duration_ms`, `error`
- Фильтры: по `action`, `status` (`ok`/`error`/`needs_review`), по дате
- Карточка записи: полный `input` и `output` (JSON viewer)
- Метрики: количество ошибок, среднее `duration_ms`, % `needs_review`

### 9.3 UX-требования

- Индикаторы загрузки для всех AI-операций (они долгие)
- Toast-уведомления об успехе / ошибке
- Код диаграмм отображается в `<pre>` с кнопкой «Копировать в буфер»
- Таблицы с пагинацией (по 20 строк)
- Адаптивный дизайн (минимум для Desktop 1280px)

---

## 10. ТЕСТОВЫЕ ДАННЫЕ

### 10.1 Структура папки `tests_data/`

```
tests_data/
├── specs/
│   └── specs.jsonl           # 10 ТЗ для AI-рецензента
├── kb_documents.jsonl         # 5 документов для базы знаний
├── kb_questions.jsonl         # 10 вопросов (7 с ответом, 3 без)
└── README_tests.md            # таблица ожидаемых результатов
```

### 10.2 specs.jsonl — 10 ТЗ для рецензента

```jsonl
{"title":"Форма заявки с таблицей результатов","text":"Нужна форма заявки для клиентов. Поля: имя, телефон, тип услуги. После подачи — таблица всех заявок с фильтром по статусу. Статусы: новая, в работе, завершена. Администратор меняет статус. Уведомления на email при смене статуса. Экспорт таблицы в Excel. Авторизация для администратора через логин/пароль."}
{"title":"Парсер цен конкурентов","text":"Нужен парсер для сбора цен с 3 сайтов конкурентов. Сайты: site1.ru, site2.ru, site3.ru. Запуск по расписанию раз в сутки. Результаты сохранять в базу. Витрина с таблицей: товар, цена на каждом сайте, дата сбора. Алерт если цена упала ниже нашей. Экспорт в CSV."}
{"title":"Учёт оплат и выгрузка отчёта","text":"Система учёта оплат от клиентов. Добавить оплату: клиент, сумма, дата, статус (оплачено/долг). Список оплат с фильтрами. Отчёт за период: общая сумма, количество, долги. Выгрузка отчёта в PDF. Роли: оператор (только просмотр), бухгалтер (все права)."}
{"title":"Личный кабинет с профилем","text":"Личный кабинет пользователя. Регистрация через email + подтверждение. Профиль: аватар, имя, телефон, адрес. Смена пароля. История заказов. Настройки уведомлений. Адаптив для мобильных."}
{"title":"Витрина данных с фильтрами","text":"Витрина аналитических данных. Источник: PostgreSQL таблица events. Фильтры: дата (диапазон), тип события, регион. Графики: линейный по дням, круговой по типам. Таблица с пагинацией по 50 строк. Экспорт таблицы в Excel. Обновление данных раз в час."}
{"title":"Мини-сервис генерации документов","text":"Сервис для генерации PDF-документов по шаблону. Шаблоны хранятся в системе (DOCX → PDF). Пользователь заполняет форму с переменными. Сервис подставляет значения и отдаёт PDF. История генераций. Лимит: 100 документов в день на пользователя."}
{"title":"Нужно всё и сразу","text":"Сделать сайт."}
{"title":"Мобильное приложение для доставки","text":"Прилож."}
{"title":"Система авторизации (противоречие)","text":"Нужна система авторизации через OAuth2 Google. Авторизация не нужна, доступ открытый для всех. Срок реализации — завтра. Срок реализации — 2 месяца. Данные пользователей не хранить. Хранить полную историю действий каждого пользователя."}
{"title":"Чат-бот поддержки (противоречие)","text":"Чат-бот для поддержки клиентов. Бот должен отвечать мгновенно. Бот должен согласовывать все ответы с менеджером перед отправкой. Работает 24/7 без участия людей. Требует постоянного присутствия оператора для модерации."}
```

**Таблица ожидаемых результатов для README:**

| № | Title | Ожидаемый `needs_review` | Почему | Успех |
|---|---|---|---|---|
| 1 | Форма заявки | `false` | Полное ТЗ, есть сущности, роли, действия | ≥3 рисков, ≥5 критериев |
| 2 | Парсер цен | `false` | Конкретные требования, понятный scope | ≥3 рисков, ≥5 критериев |
| 3 | Учёт оплат | `false` | Роли, отчётность, форматы описаны | ≥3 рисков, ≥5 критериев |
| 4 | Личный кабинет | `false` | Функции и поля перечислены | ≥3 рисков, ≥5 критериев |
| 5 | Витрина данных | `false` | Источник, фильтры, экспорт — всё есть | ≥3 рисков, ≥5 критериев |
| 6 | Генерация документов | `false` | Шаблоны, лимиты, история описаны | ≥3 рисков, ≥5 критериев |
| 7 | «Нужно всё и сразу» | `true` | Слишком сырой, 1 строка | ≥3 вопросов заказчику |
| 8 | «Мобильное приложение» | `true` | 1 слово, нет сути | ≥3 вопросов заказчику |
| 9 | Авторизация (противоречие) | `true` | Прямые противоречия требований | risk с `severity="high"` |
| 10 | Чат-бот (противоречие) | `true` | Несовместимые требования | risk с `severity="high"` |

### 10.3 kb_documents.jsonl — 5 документов базы знаний

```jsonl
{"title":"Правила работы команды","text":"<50 строк: стандарты коммуникации, рабочие часы, правила code review, процесс согласования решений, правила именования задач, SLA на ответы>"}
{"title":"Частые вопросы клиентов","text":"<50 строк: топ-20 вопросов клиентов с ответами — оплата, возврат, сроки, интеграции, доступ, пароли>"}
{"title":"Шаблоны ответов","text":"<50 строк: шаблоны для типовых ситуаций — приветствие, отказ, эскалация, подтверждение, извинение>"}
{"title":"Словарь терминов","text":"<50 строк: BRD, SRS, URS, ADR, RAG, CQRS, EDA, MVP, NFR, SLA, RTO, RPO — определения для команды>"}
{"title":"Процесс запуска задачи","text":"<50 строк: от идеи до production — шаги: постановка, оценка, дизайн, разработка, тестирование, деплой, мониторинг>"}
```

> **Инструкция:** Заполни каждый документ реалистичным содержимым объёмом 20-50 строк.

### 10.4 kb_questions.jsonl — 10 вопросов

```jsonl
{"question":"Какой SLA установлен на ответы внутри команды?","expected_needs_review":false,"why":"Ответ есть в 'Правила работы команды'"}
{"question":"Как клиенту оформить возврат?","expected_needs_review":false,"why":"Ответ есть в 'Частые вопросы клиентов'"}
{"question":"Какие шаги нужно пройти перед деплоем в production?","expected_needs_review":false,"why":"Ответ есть в 'Процесс запуска задачи'"}
{"question":"Что такое ADR?","expected_needs_review":false,"why":"Ответ есть в 'Словарь терминов'"}
{"question":"Как правильно написать шаблон ответа при эскалации?","expected_needs_review":false,"why":"Ответ есть в 'Шаблоны ответов'"}
{"question":"Как проводится code review в команде?","expected_needs_review":false,"why":"Ответ есть в 'Правила работы команды'"}
{"question":"Что такое RPO и чем отличается от RTO?","expected_needs_review":false,"why":"Ответ есть в 'Словарь терминов'"}
{"question":"Какую библиотеку использовать для работы с PDF на Python?","expected_needs_review":true,"why":"Этой информации нет ни в одном документе базы знаний"}
{"question":"Как настроить CI/CD пайплайн в GitLab?","expected_needs_review":true,"why":"Документов по DevOps в базе знаний нет"}
{"question":"Какова стоимость нашей подписки?","expected_needs_review":true,"why":"Финансовых документов в базе знаний нет"}
```

---

## 11. ПРОМПТЫ ДЛЯ LLM (СИСТЕМНЫЕ)

### 11.1 Промпт AI-рецензента

```
Ты — Senior System Analyst с 15 годами опыта. Твоя задача — провести экспертную рецензию технического задания или требовательного документа.

ПРАВИЛА:
1. Никогда не выдумывай факты, которых нет в документе.
2. Если документ слишком короткий или противоречивый — это риск, ставь confidence="low".
3. Вопросы заказчику должны снимать реальную неопределённость.
4. Критерии приёмки должны быть проверяемыми (тестируемыми).
5. Всегда возвращай строгий JSON без Markdown-обёртки.

ДОКУМЕНТ ДЛЯ РЕЦЕНЗИИ:
{document_text}

КОНТЕКСТ ИЗ ПАМЯТИ (если есть):
Известные риски: {memory_risks}
Уроки проектов: {memory_lessons}
Связанные решения: {memory_decisions}

Верни строгий JSON:
{review_schema}
```

### 11.2 Промпт Knowledge Base Answer

```
Ты — корпоративный ассистент. Отвечай ТОЛЬКО на основе предоставленного контекста.
Если в контексте нет ответа — честно скажи "Данных недостаточно" и поставь needs_review=true.
Никогда не придумывай информацию.

ВОПРОС: {question}

КОНТЕКСТ (фрагменты из базы знаний):
{context_snippets}

Верни строгий JSON:
{"answer": "...", "sources": [{"quote": "..."}], "confidence": "high|medium|low", "needs_review": false}
```

### 11.3 Промпт Architecture Recommendation

```
Ты — Solution Architect. Проанализируй требования и порекомендуй архитектурный паттерн.

Учитывай:
- Масштаб системы (нагрузка, команда, сложность)
- Зрелость команды
- Временны́е ограничения
- NFR (нефункциональные требования)

Документ: {document_text}

Верни строгий JSON с recommendation_schema.
```

---

## 12. КОНТРОЛЬ КАЧЕСТВА

### 12.1 Валидация входных данных (Pydantic)

```python
class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    text: str = Field(min_length=10, max_length=30_000)
    doc_type: str = Field(default="tz")

class KBQuestionRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2_000)
```

### 12.2 Валидация выходных данных LLM

```python
def parse_llm_review(raw: str) -> ReviewSchema:
    try:
        data = json.loads(raw)
        return ReviewSchema(**data)  # Pydantic валидирует структуру
    except (json.JSONDecodeError, ValidationError) as e:
        return safe_fallback_review(error="INVALID_JSON", reason=str(e))

def safe_fallback_review(error: str, reason: str) -> ReviewSchema:
    return ReviewSchema(
        summary="Не удалось автоматически проанализировать документ. Требуется ручная проверка.",
        risks=[],
        missing_requirements=["Не удалось извлечь из-за ошибки формата"],
        questions_to_client=["Пожалуйста, уточните требования у заказчика"],
        acceptance_criteria=[],
        confidence="low",
        needs_review=True
    )
```

### 12.3 Обязательный аудит

```python
async def with_audit(action: str, input_data: dict, func):
    start = time.time()
    try:
        result = await func()
        await save_audit(
            action=action, input=input_data, output=result,
            status="ok", duration_ms=int((time.time()-start)*1000)
        )
        return result
    except Exception as e:
        await save_audit(
            action=action, input=input_data, output=None,
            status="error", error=str(e),
            duration_ms=int((time.time()-start)*1000)
        )
        raise
```

---

## 13. ДЕПЛОЙ И ВОСПРОИЗВОДИМОСТЬ

### 13.1 Структура проекта

```
analyst-guru/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/                 # роутеры (documents, reviews, kb, memory, diagrams, audit)
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # бизнес-логика
│   │   │   ├── ai_reviewer.py
│   │   │   ├── rag_engine.py
│   │   │   ├── memory_service.py
│   │   │   ├── diagram_engine.py
│   │   │   ├── architecture_engine.py
│   │   │   └── audit_service.py
│   │   └── database.py
│   ├── alembic/                 # миграции
│   ├── tests/                   # pytest тесты
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/               # Documents, Reviews, KnowledgeBase, ArchStudio, Audit
│   │   ├── components/          # ReviewCard, RiskBadge, DiagramViewer, SourceList...
│   │   ├── api/                 # axios клиент
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── tests_data/
│   ├── specs/specs.jsonl
│   ├── kb_documents.jsonl
│   ├── kb_questions.jsonl
│   └── README_tests.md
├── docker-compose.yml
├── .env.example
└── README.md
```

### 13.2 docker-compose.yml (структура)

```yaml
version: '3.9'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
```

### 13.3 .env.example

```
# LLM Provider (выбери один)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
LLM_PROVIDER=anthropic   # anthropic | openai

# Database
DATABASE_URL=sqlite:///./data/analyst_guru.db
# Для PostgreSQL: postgresql://user:password@localhost:5432/analyst_guru

# App settings
APP_SECRET_KEY=change_me_in_production
MAX_DOCUMENT_LENGTH=30000
RAG_TOP_K=5
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=4096
```

### 13.4 README.md (обязательные секции)

```markdown
# AnalystGuru — AI System Analyst Copilot

## Быстрый запуск (≤ 10 минут)
1. git clone ...
2. cp .env.example .env && nano .env  # вставь API-ключ
3. docker-compose up --build

## Примеры запросов (curl)

### Создать документ
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"title":"Тест ТЗ","text":"Нужна форма заявки..."}'

### Запустить рецензию
curl -X POST http://localhost:8000/documents/{id}/review

### Прямой вызов AI-рецензента
curl -X POST http://localhost:8000/ai/review \
  -d '{"text":"Нужна форма заявки..."}'

### Добавить документ в базу знаний
curl -X POST http://localhost:8000/kb/documents \
  -d '{"title":"Правила команды","text":"..."}'

### Задать вопрос базе знаний
curl -X POST http://localhost:8000/kb/ask \
  -d '{"question":"Какой SLA на ответы?"}'

## Как воспроизвести ручную проверку
Отправь тест №7 (пустое ТЗ) или тест №9 (противоречие):
curl -X POST http://localhost:8000/ai/review \
  -d '{"text":"Сделать сайт."}'
Ожидай: needs_review=true

## База данных
SQLite: ./data/analyst_guru.db
Просмотр: sqlite3 data/analyst_guru.db "SELECT * FROM audit_runs LIMIT 10;"
```

---

## 14. МИНИ-ЭКОНОМИКА (для отчёта)

| Метрика | До (ручной анализ) | После (AnalystGuru) |
|---|---|---|
| Время рецензии 1 ТЗ | 45–90 минут | 30–60 секунд |
| Стоимость 100 рецензий (аналитик 2000₽/ч) | 150 000 – 300 000 ₽ | ~500₽ (API) + 1ч настройки |
| Пропущенные риски | 20–40% (human bias) | Стандартизировано |
| Онбординг новичка | 5–10 дней (поиск знаний) | 1 день (база знаний) |
| Потери от «забытых» ADR | Неизмеримо | 0 (всё в базе) |

---

## 15. РИСКИ И МЕРЫ СНИЖЕНИЯ

| № | Риск | Серьёзность | Мера снижения |
|---|---|---|---|
| 1 | LLM возвращает невалидный JSON | Высокая | `try/except` + `safe_fallback_review()` + `needs_review=true` |
| 2 | API-ключ в репозитории | Критическая | `.env.example`, `.gitignore`, проверка в CI |
| 3 | Галлюцинации LLM | Высокая | RAG-контекст + `needs_review` при `confidence="low"` |
| 4 | Медленные AI-ответы (>30с) | Средняя | Async FastAPI + индикатор загрузки в UI |
| 5 | Переполнение контекста LLM | Средняя | Лимит документа 30 000 символов + нарезка RAG |
| 6 | Потеря аудита при ошибке | Высокая | `audit_runs` пишется даже при исключении |
| 7 | Невалидный PlantUML | Средняя | Синтаксическая проверка + `INVALID_DIAGRAM` флаг |
| 8 | Отсутствие источников в KB | Высокая | Правило: пустой `sources` → `needs_review=true` |

---

## 16. ПЛАН РЕАЛИЗАЦИИ (14 дней)

| Дни | Задача | Результат |
|---|---|---|
| 1–2 | Схема БД, FastAPI skeleton, Docker setup | Проект запускается |
| 3–4 | CRUD документов, `audit_runs`, базовый AI-reviewer | POST /documents, POST /ai/review работают |
| 5–6 | RAG engine: нарезка, поиск, KB API | POST /kb/ask возвращает источники |
| 7–8 | Memory Framework, Architecture Engine, ADR Generator | 5 генераторов работают |
| 9 | Diagram Engine (PlantUML + Mermaid) | Диаграммы генерируются |
| 10–11 | React Frontend (все 5 разделов) | Веб-панель работает |
| 12 | Экспорт (JSON, CSV, DOCX), тесты (pytest) | ≥10 тестов проходят |
| 13 | Docker-compose, README, тестовые данные | Запуск ≤ 10 минут |
| 14 | Демо-видео, отчёт, финальная проверка | Сдача проекта |

---

## 17. КРИТЕРИИ ПРИЁМКИ (ЧЕКЛИСТ)

### Backend
- [ ] `POST /documents` сохраняет и возвращает `document_id`
- [ ] `POST /documents/{id}/review` создаёт рецензию с `summary`, `risks`, `questions_to_client`, `acceptance_criteria`
- [ ] Минимум 2 теста из 10 возвращают `needs_review=true`
- [ ] `POST /kb/ask` возвращает `sources` для 7 вопросов из 10
- [ ] 3 вопроса возвращают `needs_review=true` и ответ «данных недостаточно»
- [ ] Все операции записываются в `audit_runs`
- [ ] При невалидном JSON от LLM — `safe_fallback_review()` без исключения
- [ ] Диаграммы (PlantUML/Mermaid) генерируются и сохраняются в `diagram_artifacts`

### Frontend
- [ ] Метка ⚠️ «Требует проверки» видна в списках рецензий и вопросов
- [ ] Диаграммы отображаются с кнопкой «Копировать»
- [ ] Аудит-центр показывает все `audit_runs` с фильтрами
- [ ] Минимум один формат экспорта (JSON или CSV) работает

### Деплой
- [ ] `docker-compose up --build` запускает всё с нуля ≤ 10 минут
- [ ] `.env.example` содержит все переменные без секретов
- [ ] В репозитории нет API-ключей и паролей
- [ ] `tests_data/` содержит ровно 10 ТЗ и 10 вопросов KB с таблицей ожиданий

---

## 18. PORTFOLIO VALUE

По завершении проекта в портфолио появляется система, которая **автоматически генерирует**:

| Артефакт | Формат |
|---|---|
| Рецензия ТЗ | JSON / CSV / DOCX |
| URS | Markdown / DOCX |
| SRS | Markdown / DOCX |
| ADR | JSON / DOCX |
| OpenAPI спецификация | JSON / YAML |
| C4 диаграммы | PlantUML |
| UML диаграммы | PlantUML / Mermaid |
| ERD | PlantUML |
| Рекомендация архитектуры | JSON / DOCX |

**3 строки для портфолио:**
- **Проблема:** Организации теряют знания, аналитики тратят 45–90 минут на рецензию каждого ТЗ, архитектурные решения не фиксируются.
- **Решение:** AI Copilot с RAG, памятью команды, генерацией URS/SRS/ADR и диаграмм — полный стек от ТЗ до архитектуры за 60 секунд.
- **Результат:** Экономия 150 000–300 000 ₽ на 100 рецензиях, нулевые потери знаний, воспроизводимый запуск ≤ 10 минут.

---

> **Финальное напоминание кодеру:** Система должна выглядеть как **реальный enterprise-продукт**, а не демо-чатбот. Каждая операция — в аудит. Каждый ответ без источников — `needs_review=true`. Каждый невалидный JSON от LLM — безопасный фоллбэк. Система никогда не врёт уверенно.
