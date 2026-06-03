import { createContext, useContext, useState, ReactNode } from "react";

export type Lang = "ru" | "en";

const translations = {
  ru: {
    // nav
    nav_dashboard: "Дашборд",
    nav_documents: "Документы",
    nav_reviews: "Рецензии",
    nav_knowledge_base: "База знаний",
    nav_architecture: "Архитектура",
    nav_memory: "Память",
    nav_audit: "Аудит",

    // dashboard
    dashboard_title: "Дашборд",
    dashboard_subtitle: "Статус системы и последние операции аналитика.",
    dashboard_new_doc: "Новый документ",
    dashboard_start_review: "Начать рецензию",
    dashboard_total_docs: "Всего документов",
    dashboard_managed_in_system: "Управляется в системе",
    dashboard_reviews_performed: "Проведено рецензий",
    dashboard_ai_analyses: "AI-анализы",
    dashboard_needs_review: "Требует проверки",
    dashboard_items_requiring_check: "Элементы для ручной проверки",
    dashboard_knowledge_base: "База знаний",
    dashboard_indexed_artifacts: "Индексированные материалы",
    dashboard_recent_activity: "Последние операции",
    dashboard_latest_ops: "Последние системные операции и AI-генерации.",
    dashboard_no_activity: "Активности не найдено.",
    dashboard_quick_workflows: "Быстрые действия",
    dashboard_common_ops: "Частые операции",
    dashboard_browse_docs: "Просмотр документов",
    dashboard_pending_reviews: "Ожидающие рецензии",
    dashboard_ask_kb: "Спросить базу знаний",
    dashboard_design_arch: "Проектировать архитектуру",
    needs_review_badge: "⚠️ Требует проверки",

    // documents
    docs_title: "Документы",
    docs_subtitle: "Управление и рецензирование проектной документации.",
    docs_add: "Добавить документ",
    docs_add_title: "Добавить новый документ",
    docs_title_field: "Название",
    docs_type_field: "Тип",
    docs_project_field: "Название проекта (опционально)",
    docs_content_field: "Содержимое",
    docs_title_placeholder: "Например: Требования к платёжному шлюзу",
    docs_project_placeholder: "Проект Альфа",
    docs_content_placeholder: "Вставьте содержимое документа...",
    docs_select_type: "Выберите тип",
    docs_cancel: "Отмена",
    docs_saving: "Сохранение...",
    docs_save: "Сохранить",
    docs_col_title: "Название",
    docs_col_type: "Тип",
    docs_col_project: "Проект",
    docs_col_created: "Создан",
    docs_col_actions: "Действия",
    docs_view: "Открыть",
    docs_empty: "Документы не найдены.",
    docs_created_success: "Документ создан",
    docs_create_error: "Ошибка создания",

    // document detail
    doc_detail_no_project: "Без проекта",
    doc_detail_run_review: "Запустить AI-рецензию",
    doc_detail_delete: "Удалить",
    doc_detail_content: "Содержимое",
    doc_detail_not_found: "Документ не найден",
    doc_detail_delete_confirm: "Удалить этот документ?",
    doc_detail_deleted: "Документ удалён",
    doc_detail_delete_error: "Ошибка удаления",
    doc_detail_review_done: "Рецензия завершена",
    doc_detail_review_error: "Ошибка рецензии",

    // reviews
    reviews_title: "AI-рецензии",
    reviews_subtitle: "Результаты анализа и проверки документов.",
    reviews_col_doc: "Документ",
    reviews_col_status: "Статус",
    reviews_col_confidence: "Уверенность",
    reviews_col_created: "Создана",
    reviews_col_actions: "Действия",
    reviews_view: "Просмотр",
    reviews_empty: "Рецензии не найдены.",
    reviews_ok: "OK",

    // review detail
    review_detail_title: "Детали рецензии",
    review_detail_for_doc: "Для документа:",
    review_detail_confidence: "Уверенность:",
    review_detail_summary: "Резюме",
    review_detail_risks: "Выявленные риски",
    review_detail_missing_req: "Отсутствующие требования",
    review_detail_questions: "Вопросы заказчику",
    review_detail_criteria: "Критерии приёмки",
    review_detail_no_risks: "Риски не выявлены.",
    review_detail_no_req: "Не найдено.",
    review_detail_no_questions: "Вопросы не сформированы.",
    review_detail_no_criteria: "Не указаны.",
    review_detail_not_found: "Рецензия не найдена",
    review_export_json: "Экспорт JSON",
    review_export_csv: "Экспорт CSV",
    review_detail_export_title: "Экспорт",
    docs_run_review: "Рецензия",
    docs_review_running: "Запуск...",

    // knowledge base
    kb_title: "База знаний",
    kb_subtitle: "RAG-поиск по индексированным материалам.",
    kb_tab_ask: "Спросить AI",
    kb_tab_docs: "Индексированные документы",
    kb_tab_history: "История Q&A",
    kb_ask_title: "Задать вопрос",
    kb_ask_desc: "Поиск по всей проектной документации и принятым решениям.",
    kb_ask_placeholder: "Например: Какой механизм аутентификации в Проекте Альфа?",
    kb_ask_btn: "Спросить",
    kb_answer_title: "Ответ",
    kb_sources: "ИСТОЧНИКИ",
    kb_unknown_doc: "Неизвестный документ",
    kb_docs_col_title: "Название",
    kb_docs_col_id: "ID",
    kb_docs_col_project: "Проект",
    kb_docs_col_added: "Добавлен",
    kb_docs_col_actions: "Действия",
    kb_docs_add: "Добавить документ",
    kb_docs_add_title: "Добавить документ в базу знаний",
    kb_docs_open: "Открыть",
    kb_docs_empty: "Нет документов в базе знаний.",
    kb_docs_add_success: "Документ добавлен в базу знаний",
    kb_docs_add_error: "Ошибка добавления документа",
    kb_history_col_question: "Вопрос",
    kb_history_col_status: "Статус",
    kb_history_col_asked: "Время",
    kb_history_col_actions: "Действия",
    kb_history_filter_all: "Все",
    kb_history_filter_needs_review: "Требует проверки",
    kb_history_open: "Открыть ответ",
    kb_history_detail_title: "Детали вопроса",
    kb_history_detail_answer: "Ответ",
    kb_history_detail_sources: "Источники",
    kb_history_detail_error: "Причина ручной проверки",
    kb_history_empty: "История отсутствует.",

    // architecture studio
    arch_title: "Архитектурная студия",
    arch_subtitle: "Проектирование архитектур, API и ADR.",
    arch_tab_c4: "C4-диаграммы",
    arch_tab_uml: "UML",
    arch_tab_erd: "ERD",
    arch_tab_api: "API-дизайн",
    arch_tab_adr: "ADR",
    arch_tab_recs: "Рекомендации",
    arch_c4_title: "Генерация C4-диаграмм",
    arch_c4_hint: "Выберите документ для генерации диаграмм Context, Container и Component.",

    // memory
    memory_title: "Фреймворк памяти",
    memory_subtitle: "Семантический граф знаний в масштабе проекта.",
    memory_search_title: "Поиск в памяти",
    memory_search_placeholder: "Поиск концепций, решений, ограничений...",
    memory_search_btn: "Найти",
    memory_empty: "По вашему запросу ничего не найдено.",
    memory_score: "Оценка:",

    // settings
    nav_settings: "Настройки",
    settings_title: "Настройки AI",
    settings_subtitle: "Управление AI-провайдерами и API-ключами.",
    settings_ai_title: "AI-провайдер",
    settings_ai_desc: "Выберите провайдера и введите API-ключ для работы AI-операций.",
    settings_provider: "Провайдер",
    settings_api_key: "API-ключ",
    settings_key_placeholder_set: "Введите новый ключ (оставьте пустым чтобы сохранить текущий)",
    settings_key_placeholder_empty: "Введите API-ключ провайдера",
    settings_key_current: "API-ключ установлен",
    settings_save_btn: "Сохранить настройки",
    settings_saved: "Настройки сохранены",
    settings_error: "Ошибка сохранения настроек",

    // audit
    audit_title: "Центр аудита",
    audit_subtitle: "Телеметрия системы и журналы выполнения.",
    audit_col_action: "Операция",
    audit_col_status: "Статус",
    audit_col_duration: "Длительность",
    audit_col_executed: "Выполнено",
    audit_empty: "Журналы аудита не найдены.",

    // common
    common_loading: "Загрузка...",
    common_page: "Страница",
    common_prev: "Назад",
    common_next: "Вперёд",
    common_search: "Поиск",
    system_core: "System Core v1.0.4",
  },
  en: {
    // nav
    nav_dashboard: "Dashboard",
    nav_documents: "Documents",
    nav_reviews: "Reviews",
    nav_knowledge_base: "Knowledge Base",
    nav_architecture: "Architecture",
    nav_memory: "Memory",
    nav_audit: "Audit Center",

    // dashboard
    dashboard_title: "Dashboard",
    dashboard_subtitle: "System status and recent analyst activities.",
    dashboard_new_doc: "New Document",
    dashboard_start_review: "Start Review",
    dashboard_total_docs: "Total Documents",
    dashboard_managed_in_system: "Managed in system",
    dashboard_reviews_performed: "Reviews Performed",
    dashboard_ai_analyses: "AI-assisted analyses",
    dashboard_needs_review: "Needs Review",
    dashboard_items_requiring_check: "Items requiring human check",
    dashboard_knowledge_base: "Knowledge Base",
    dashboard_indexed_artifacts: "Indexed artifacts",
    dashboard_recent_activity: "Recent Activity",
    dashboard_latest_ops: "Latest system operations and AI generations.",
    dashboard_no_activity: "No recent activity found.",
    dashboard_quick_workflows: "Quick Workflows",
    dashboard_common_ops: "Common operations",
    dashboard_browse_docs: "Browse Documents",
    dashboard_pending_reviews: "Pending Reviews",
    dashboard_ask_kb: "Ask Knowledge Base",
    dashboard_design_arch: "Design Architecture",
    needs_review_badge: "⚠️ Needs Review",

    // documents
    docs_title: "Documents",
    docs_subtitle: "Manage and review project documentation.",
    docs_add: "Add Document",
    docs_add_title: "Add New Document",
    docs_title_field: "Title",
    docs_type_field: "Type",
    docs_project_field: "Project Name (Optional)",
    docs_content_field: "Content",
    docs_title_placeholder: "E.g. Payment Gateway Requirements",
    docs_project_placeholder: "Project Alpha",
    docs_content_placeholder: "Paste document content here...",
    docs_select_type: "Select type",
    docs_cancel: "Cancel",
    docs_saving: "Saving...",
    docs_save: "Save Document",
    docs_col_title: "Title",
    docs_col_type: "Type",
    docs_col_project: "Project",
    docs_col_created: "Created At",
    docs_col_actions: "Actions",
    docs_view: "View",
    docs_empty: "No documents found.",
    docs_created_success: "Document created successfully",
    docs_create_error: "Failed to create document",

    // document detail
    doc_detail_no_project: "No Project",
    doc_detail_run_review: "Run AI Review",
    doc_detail_delete: "Delete",
    doc_detail_content: "Content",
    doc_detail_not_found: "Document not found",
    doc_detail_delete_confirm: "Are you sure you want to delete this document?",
    doc_detail_deleted: "Document deleted",
    doc_detail_delete_error: "Failed to delete",
    doc_detail_review_done: "Review completed",
    doc_detail_review_error: "Review failed",

    // reviews
    reviews_title: "AI Reviews",
    reviews_subtitle: "Analysis results and document checks.",
    reviews_col_doc: "Document",
    reviews_col_status: "Status",
    reviews_col_confidence: "Confidence",
    reviews_col_created: "Created At",
    reviews_col_actions: "Actions",
    reviews_view: "View Details",
    reviews_empty: "No reviews found.",
    reviews_ok: "OK",

    // review detail
    review_detail_title: "Review Details",
    review_detail_for_doc: "For document:",
    review_detail_confidence: "Confidence:",
    review_detail_summary: "Summary",
    review_detail_risks: "Identified Risks",
    review_detail_missing_req: "Missing Requirements",
    review_detail_questions: "Questions to Client",
    review_detail_criteria: "Acceptance Criteria",
    review_detail_no_risks: "No risks identified.",
    review_detail_no_req: "None found.",
    review_detail_no_questions: "No questions generated.",
    review_detail_no_criteria: "Not specified.",
    review_detail_not_found: "Review not found",
    review_export_json: "Export JSON",
    review_export_csv: "Export CSV",
    review_detail_export_title: "Export",
    docs_run_review: "Review",
    docs_review_running: "Running...",

    // knowledge base
    kb_title: "Knowledge Base",
    kb_subtitle: "RAG-powered search across indexed artifacts.",
    kb_tab_ask: "Ask AI",
    kb_tab_docs: "Indexed Documents",
    kb_tab_history: "Q&A History",
    kb_ask_title: "Ask a Question",
    kb_ask_desc: "Search across all project documentation and decisions.",
    kb_ask_placeholder: "E.g. What is the authentication mechanism for Project Alpha?",
    kb_ask_btn: "Ask",
    kb_answer_title: "Answer",
    kb_sources: "SOURCES",
    kb_unknown_doc: "Unknown Document",
    kb_docs_col_title: "Title",
    kb_docs_col_id: "ID",
    kb_docs_col_project: "Project",
    kb_docs_col_added: "Added",
    kb_docs_col_actions: "Actions",
    kb_docs_add: "Add Document",
    kb_docs_add_title: "Add Document to Knowledge Base",
    kb_docs_open: "Open",
    kb_docs_empty: "No documents in KB.",
    kb_docs_add_success: "Document added to knowledge base",
    kb_docs_add_error: "Failed to add document",
    kb_history_col_question: "Question",
    kb_history_col_status: "Status",
    kb_history_col_asked: "Asked At",
    kb_history_col_actions: "Actions",
    kb_history_filter_all: "All",
    kb_history_filter_needs_review: "Needs Review",
    kb_history_open: "View Answer",
    kb_history_detail_title: "Question Details",
    kb_history_detail_answer: "Answer",
    kb_history_detail_sources: "Sources",
    kb_history_detail_error: "Reason for manual check",
    kb_history_empty: "No history.",

    // architecture studio
    arch_title: "Architecture Studio",
    arch_subtitle: "Design system architectures, APIs, and ADRs.",
    arch_tab_c4: "C4 Diagrams",
    arch_tab_uml: "UML",
    arch_tab_erd: "ERD",
    arch_tab_api: "API Design",
    arch_tab_adr: "ADRs",
    arch_tab_recs: "Recommendations",
    arch_c4_title: "Generate C4 Diagrams",
    arch_c4_hint: "Select a document to generate Context, Container, and Component diagrams.",

    // memory
    memory_title: "Memory Framework",
    memory_subtitle: "Semantic knowledge graph across project scope.",
    memory_search_title: "Search Memory",
    memory_search_placeholder: "Search concepts, decisions, constraints...",
    memory_search_btn: "Search",
    memory_empty: "No memories matched your search.",
    memory_score: "Score:",

    // settings
    nav_settings: "Settings",
    settings_title: "AI Settings",
    settings_subtitle: "Manage AI providers and API keys.",
    settings_ai_title: "AI Provider",
    settings_ai_desc: "Select provider and enter API key for AI operations.",
    settings_provider: "Provider",
    settings_api_key: "API Key",
    settings_key_placeholder_set: "Enter new key (leave empty to keep current)",
    settings_key_placeholder_empty: "Enter provider API key",
    settings_key_current: "API key is set",
    settings_save_btn: "Save Settings",
    settings_saved: "Settings saved",
    settings_error: "Failed to save settings",

    // audit
    audit_title: "Audit Center",
    audit_subtitle: "System telemetry and execution logs.",
    audit_col_action: "Action",
    audit_col_status: "Status",
    audit_col_duration: "Duration",
    audit_col_executed: "Executed At",
    audit_empty: "No audit logs found.",

    // common
    common_loading: "Loading...",
    common_page: "Page",
    common_prev: "Previous",
    common_next: "Next",
    common_search: "Search",
    system_core: "System Core v1.0.4",
  },
} as const;

export type TranslationKey = keyof typeof translations.ru;

interface LanguageContextType {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: typeof translations.ru;
}

const LanguageContext = createContext<LanguageContextType | null>(null);

function getInitialLang(): Lang {
  try {
    const stored = localStorage.getItem("analyst-guru-lang");
    if (stored === "en" || stored === "ru") return stored;
  } catch {}
  return "ru";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang);

  const setLang = (l: Lang) => {
    setLangState(l);
    try { localStorage.setItem("analyst-guru-lang", l); } catch {}
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t: translations[lang] }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
