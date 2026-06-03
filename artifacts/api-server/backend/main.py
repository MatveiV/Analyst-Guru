import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.api import documents, reviews, kb, generators, memory, diagrams, audit, dashboard, settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AnalystGuru API",
    description="AI System Analyst Copilot — REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing database tables...")
    try:
        init_db()
        logger.info("Database tables ready")
        _seed_demo_data()
    except Exception as e:
        logger.error(f"Startup error: {e}")


def _seed_demo_data():
    from backend.database import SessionLocal
    from backend.models import Document as DocumentModel, MemoryItem
    import json

    db = SessionLocal()
    try:
        existing_count = db.query(DocumentModel).count()
        if existing_count > 0:
            return

        kb_docs = [
            {
                "title": "Правила работы команды",
                "text": """Стандарты коммуникации команды AnalystGuru:

1. Общение: Все рабочие вопросы решаются в корпоративном мессенджере в рабочее время (9:00-18:00 МСК).
2. SLA на ответы: Внутри команды — до 2 часов в рабочее время. Клиентские запросы — до 4 часов.
3. Code Review: Каждый PR проходит ревью минимум 2 участников. Ревьюер должен ответить в течение 24 часов.
4. Процесс согласования: Архитектурные решения оформляются в виде ADR и согласуются с Lead-архитектором.
5. Именование задач: [PROJECT]-[НОМЕР]: Краткое описание. Например: AG-123: Добавить эндпоинт генерации диаграмм.
6. Документирование: Все изменения API фиксируются в OpenAPI спецификации до начала разработки.
7. Ретроспективы: Проводятся каждые 2 недели по пятницам в 16:00.
8. Onboarding: Новый сотрудник должен прочитать всю документацию в базе знаний в первый день.
9. Эскалация: При блокирующей проблеме — немедленно уведомить тимлида, не ждать до стендапа.
10. Стендап: Ежедневно в 10:00 МСК, формат: что сделал вчера / что планирую сегодня / блокеры.""",
                "doc_type": "kb_article",
                "is_kb": True,
            },
            {
                "title": "Частые вопросы клиентов",
                "text": """Топ-20 вопросов клиентов и ответы на них:

1. Q: Как оплатить? A: Оплата банковской картой, СБП или счётом для юридических лиц через личный кабинет.
2. Q: Как оформить возврат? A: Через раздел «Мои заказы» → «Запросить возврат». Срок рассмотрения — 3 рабочих дня.
3. Q: Какие сроки доставки? A: Стандарт — 3-5 рабочих дней, экспресс — 1 рабочий день (доступно в Москве и СПб).
4. Q: Как получить доступ? A: После оплаты доступ выдаётся автоматически на email, указанный при регистрации.
5. Q: Забыл пароль? A: Используйте форму «Восстановить пароль» на странице входа.
6. Q: Есть ли API для интеграции? A: Да, OpenAPI документация доступна по адресу /api/docs.
7. Q: Как добавить пользователей в команду? A: Настройки → Команда → Пригласить участника.
8. Q: Как экспортировать данные? A: Раздел Отчёты → Экспорт → выберите формат (CSV, XLSX, PDF).
9. Q: Где хранятся мои данные? A: На серверах в России (ЦОД Tier III в Москве), данные шифруются AES-256.
10. Q: Как отменить подписку? A: Настройки → Подписка → Отменить. Доступ сохраняется до конца оплаченного периода.""",
                "doc_type": "kb_article",
                "is_kb": True,
            },
            {
                "title": "Словарь терминов",
                "text": """Глоссарий терминов для команды:

BRD (Business Requirements Document) — документ бизнес-требований, описывающий цели и задачи бизнеса.
SRS (Software Requirements Specification) — спецификация требований к программному обеспечению по стандарту IEEE 830.
URS (User Requirements Specification) — спецификация требований пользователей, описывает что система должна делать с точки зрения пользователя.
ADR (Architecture Decision Record) — запись об архитектурном решении с контекстом, проблемой, решением и последствиями.
RAG (Retrieval-Augmented Generation) — метод генерации ответов LLM с использованием найденного контекста из базы знаний.
CQRS (Command Query Responsibility Segregation) — паттерн разделения команд и запросов.
EDA (Event-Driven Architecture) — событийно-ориентированная архитектура.
MVP (Minimum Viable Product) — минимально жизнеспособный продукт.
NFR (Non-Functional Requirements) — нефункциональные требования (производительность, безопасность, доступность).
SLA (Service Level Agreement) — соглашение об уровне сервиса.
RTO (Recovery Time Objective) — целевое время восстановления после сбоя.
RPO (Recovery Point Objective) — целевая точка восстановления данных (максимально допустимая потеря данных).
CI/CD — непрерывная интеграция и непрерывная доставка.
TDD (Test-Driven Development) — разработка через тестирование.
DDD (Domain-Driven Design) — предметно-ориентированное проектирование.""",
                "doc_type": "kb_article",
                "is_kb": True,
            },
        ]

        for kb_doc in kb_docs:
            doc = DocumentModel(**kb_doc)
            db.add(doc)
        db.flush()

        sample_docs = [
            {
                "title": "Форма заявки с таблицей результатов",
                "text": "Нужна форма заявки для клиентов. Поля: имя, телефон, тип услуги. После подачи — таблица всех заявок с фильтром по статусу. Статусы: новая, в работе, завершена. Администратор меняет статус. Уведомления на email при смене статуса. Экспорт таблицы в Excel. Авторизация для администратора через логин/пароль.",
                "doc_type": "tz",
                "is_kb": False,
            },
            {
                "title": "Парсер цен конкурентов",
                "text": "Нужен парсер для сбора цен с 3 сайтов конкурентов. Запуск по расписанию раз в сутки. Результаты сохранять в базу. Витрина с таблицей: товар, цена на каждом сайте, дата сбора. Алерт если цена упала ниже нашей. Экспорт в CSV.",
                "doc_type": "tz",
                "is_kb": False,
            },
        ]

        for sd in sample_docs:
            doc = DocumentModel(**sd)
            db.add(doc)

        memory_seeds = [
            {
                "memory_type": "semantic",
                "content": "При проектировании систем с ролями (admin/operator/user) всегда предусматривать матрицу доступа RBAC.",
                "tags": json.dumps(["security", "rbac", "roles"]),
            },
            {
                "memory_type": "risk",
                "content": "[HIGH] Противоречивые требования в ТЗ ведут к многократным переделкам. Признак: в одном документе утверждение и его отрицание.",
                "tags": json.dumps(["requirements", "contradiction"]),
            },
            {
                "memory_type": "decision",
                "content": "ADR-001: Выбор PostgreSQL вместо SQLite для production. Обоснование: параллельные запросы, полнотекстовый поиск FTS, JSON-поля.",
                "tags": json.dumps(["database", "postgresql", "adr"]),
            },
        ]

        for ms in memory_seeds:
            item = MemoryItem(**ms)
            db.add(item)

        db.commit()
        logger.info("Demo data seeded successfully")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding error: {e}")
    finally:
        db.close()


@app.get("/api/healthz")
def health_check():
    return {"status": "ok"}


app.include_router(documents.router)
app.include_router(reviews.router)
app.include_router(kb.router)
app.include_router(kb.router_direct)
app.include_router(generators.router)
app.include_router(generators.router_adr)
app.include_router(generators.router_arch)
app.include_router(generators.router_specs)
app.include_router(memory.router)
app.include_router(diagrams.router)
app.include_router(audit.router)
app.include_router(dashboard.router)
app.include_router(settings.router)
