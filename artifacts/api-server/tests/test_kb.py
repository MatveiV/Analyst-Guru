import json
import pytest
from unittest.mock import patch


class TestKnowledgeBase:
    def test_add_kb_document(self, client):
        resp = client.post("/api/kb/documents", json={
            "title": "KB Test Doc",
            "text": "Тестовый документ для базы знаний. Содержит важную информацию для команды.",
            "doc_type": "kb_article",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_kb"] is True

    def test_list_kb_documents(self, client):
        client.post("/api/kb/documents", json={
            "title": "KB Doc 1",
            "text": "Первый документ базы знаний. Важные правила работы команды.",
        })
        resp = client.get("/api/kb/documents")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_ask_knowledge_base(self, client):
        client.post("/api/kb/documents", json={
            "title": "Правила работы",
            "text": "SLA на ответы внутри команды — до 2 часов в рабочее время.",
        })

        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "SLA на ответы внутри команды — до 2 часов.",
                "sources": [{"quote": "SLA на ответы внутри команды"}],
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post("/api/kb/ask", json={
                "question": "Какой SLA на ответы внутри команды?",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "answer" in data
            assert "sources" in data

    def test_kb_history(self, client):
        resp = client.get("/api/kb/history")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_direct_answer(self, client):
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "Тестовый ответ.",
                "sources": [{"quote": "Источник"}],
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post("/api/ai/answer_with_sources", json={
                "question": "Тестовый вопрос?",
                "context": "Тестовый контекст для ответа.",
            })
            assert resp.status_code == 200
            assert resp.json()["answer"] == "Тестовый ответ."
