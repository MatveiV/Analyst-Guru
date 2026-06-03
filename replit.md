# AnalystGuru — Architecture Guide

AI System Analyst Copilot — рабочий стол Lead System Analyst / Solution Architect: AI-рецензии ТЗ, RAG-база знаний, генерация URS/SRS/ADR/OpenAPI/диаграмм, память по проектам, audit-центр.

## Run & Operate

- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm run typecheck` — full typecheck across all packages
- API server runs via Python/uvicorn: `python artifacts/api-server/run.py`
- Frontend runs via Vite: `pnpm --filter @workspace/analyst-guru run dev`
- Required env: `DATABASE_URL` — Postgres connection string
- Optional env: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `LLM_PROVIDER` (default: anthropic)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React 18 + Vite + TanStack Query + Wouter + shadcn/ui
- API: Python 3.11 + FastAPI + uvicorn
- DB: PostgreSQL + SQLAlchemy 2 (Python side), Drizzle ORM (Node schema)
- LLM: Anthropic claude-3-5-sonnet-20241022 (primary), OpenAI gpt-4o (fallback), ProxyAPI (OpenAI-compatible)
- RAG: hybrid keyword + semantic search (sentence-transformers all-MiniLM-L6-v2, optional)
- API codegen: Orval (from OpenAPI spec → React Query hooks + Zod schemas)

## Where things live

- `artifacts/analyst-guru/` — React+Vite frontend, all 9 pages
- `artifacts/api-server/backend/` — Python FastAPI backend
  - `backend/main.py` — FastAPI app, startup, seed
  - `backend/models.py` — SQLAlchemy models (10 tables)
  - `backend/api/` — route modules (documents, reviews, kb, generators, memory, diagrams, audit, dashboard, settings)
  - `backend/services/ai_service.py` — LLM prompts (review, RAG, URS, SRS, ADR, OpenAPI, diagrams, architecture)
  - `backend/services/rag_engine.py` — hybrid search (keyword + semantic)
  - `backend/services/audit_service.py` — every AI call wrapped in audit
- `lib/api-spec/openapi.yaml` — OpenAPI contract (source of truth for all API shapes)
- `lib/api-client-react/` — generated React Query hooks (from codegen)
- `lib/api-zod/` — generated Zod schemas

## Architecture decisions

- Python FastAPI replaces Node.js Express for the `/api` service — AI libs (anthropic, sentence-transformers) are Python-native.
- All LLM calls are wrapped in `with_audit()` — every AI operation is recorded to `audit_runs` with input/output, status, and duration.
- `needs_review=true` propagates: low-confidence LLM output auto-flags items for human review.
- RAG is hybrid: keyword search (always works) + semantic cosine similarity (degrades gracefully if sentence-transformers unavailable).
- DB tables created via `Base.metadata.create_all()` on startup — no migration tool needed for current scale.
- AI provider (Anthropic/OpenAI/ProxyAPI) and API keys configurable via Settings page in the web UI.

## Product

**AnalystGuru** дает System Analyst-ам:
- Загрузить ТЗ → получить детальную AI-рецензию с рисками, вопросами заказчику, критериями приёмки
- База знаний (RAG): загрузить регламенты/глоссарии → задать вопрос → получить ответ со ссылками на источники
- Сгенерировать URS / SRS / ADR / OpenAPI спецификацию / C4+UML+ERD диаграммы из документа одним кликом
- Memory Framework: накапливать риски, уроки, решения по проектам
- Audit Center: видеть каждый AI-вызов с duration_ms, input/output, статусом
- Настройки AI: выбрать провайдера и ввести API-ключ

## Gotchas

- `run.py` lives in `artifacts/api-server/` and is run from that directory.
- `sentence-transformers` not installed by default — RAG falls back to keyword-only search silently.
- LLM returns sometimes wrap JSON in markdown fences — `safe_parse_json()` strips them.
- API server artifact.toml `run` command executes from `artifacts/api-server/` — use relative path `python run.py`.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
