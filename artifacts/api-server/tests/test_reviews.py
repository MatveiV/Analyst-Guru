import json
import pytest
from unittest.mock import patch


class TestReviews:
    def test_direct_ai_review(self, client):
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Тестовый обзор документа.",
                "risks": [{"severity": "medium", "description": "Тестовый риск"}],
                "missing_requirements": ["Требование 1"],
                "questions_to_client": ["Вопрос 1"],
                "acceptance_criteria": ["Критерий 1"],
                "similar_projects": [],
                "lessons_learned": [],
                "related_decisions": [],
                "architecture_risks": [],
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post("/api/ai/review", json={
                "text": "Тестовый документ для рецензии. Должен быть достаточно длинным для прохождения валидации.",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["confidence"] == "high"
            assert data["needs_review"] is False

    def test_review_document(self, client):
        create_resp = client.post("/api/documents", json={
            "title": "Review Test",
            "text": "Нужна форма заявки для клиентов. Поля: имя, телефон, тип услуги. Статусы: новая, в работе, завершена.",
        })
        doc_id = create_resp.json()["id"]

        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Обзор формы заявки.",
                "risks": [{"severity": "low", "description": "Риск 1"}],
                "missing_requirements": ["Нет поля email"],
                "questions_to_client": ["Какие ещё поля нужны?"],
                "acceptance_criteria": ["Форма работает"],
                "similar_projects": [],
                "lessons_learned": [],
                "related_decisions": [],
                "architecture_risks": [],
                "confidence": "medium",
                "needs_review": False,
            })
            resp = client.post(f"/api/documents/{doc_id}/review")
            assert resp.status_code == 201
            data = resp.json()
            assert data["document_id"] == doc_id
            assert "review_json" in data

    def test_list_reviews(self, client):
        resp = client.get("/api/reviews")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_review(self, client):
        resp = client.get("/api/reviews/nonexistent")
        assert resp.status_code == 404

    def test_export_review_json(self, client):
        create_resp = client.post("/api/documents", json={
            "title": "Export Test", "text": "Документ для экспорта. Тестирование выгрузки рецензии.",
        })
        doc_id = create_resp.json()["id"]

        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Обзор для экспорта.",
                "risks": [], "missing_requirements": [], "questions_to_client": [],
                "acceptance_criteria": [], "similar_projects": [], "lessons_learned": [],
                "related_decisions": [], "architecture_risks": [],
                "confidence": "low", "needs_review": True,
            })
            review_resp = client.post(f"/api/documents/{doc_id}/review")
            review_id = review_resp.json()["id"]

        resp = client.get(f"/api/reviews/{review_id}/export/json")
        assert resp.status_code == 200

        resp = client.get(f"/api/reviews/{review_id}/export/csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
