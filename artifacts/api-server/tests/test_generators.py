import json
from unittest.mock import patch


class TestGenerators:
    def _create_doc(self, client):
        resp = client.post("/api/documents", json={
            "title": "Test Doc for Generation",
            "text": "Тестовый документ для проверки генерации документов. Система должна поддерживать авторизацию через OAuth 2.0 и хранить данные в PostgreSQL.",
            "doc_type": "tz",
        })
        return resp.json()["id"]

    def test_generate_urs(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "content": "# URS\n## Цели\nТестовая цель",
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post(f"/api/documents/{doc_id}/generate-urs")
            assert resp.status_code == 200
            data = resp.json()
            assert data["content_type"] == "urs"
            assert "content" in data

    def test_generate_srs(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "content": "# SRS\n## Requirements\nТестовое требование",
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post(f"/api/documents/{doc_id}/generate-srs")
            assert resp.status_code == 200
            data = resp.json()
            assert data["content_type"] == "srs"
            assert "content" in data

    def test_generate_adr(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "title": "ADR-001",
                "status": "proposed",
                "context": "Выбор БД для нового сервиса",
                "problem": "Какую БД использовать",
                "decision": "PostgreSQL",
                "alternatives": [{"option": "MySQL", "reason_rejected": "Меньше опыта"}],
                "consequences": {"positive": ["Больше опыта в команде"], "negative": []},
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post(f"/api/documents/{doc_id}/generate-adr")
            assert resp.status_code == 200
            assert resp.json()["adr_json"]["decision"] == "PostgreSQL"

    def test_design_api(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {"/test": {"get": {"summary": "Test"}}},
                "openapi_yaml": "openapi: 3.0.0\ninfo:\n  title: Test API",
            })
            resp = client.post(f"/api/documents/{doc_id}/design-api")
            assert resp.status_code == 200
            data = resp.json()
            assert data["openapi_json"] is not None

    def test_recommend_architecture(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "recommended_pattern": "microservices",
                "rationale": "Подходит для масштабирования",
                "alternatives": [{"pattern": "Monolith", "pros": ["Простота"], "cons": ["Сложно масштабировать"]}],
                "integration_recommendations": ["REST API"],
                "risks": [{"severity": "medium", "description": "Сложность инфраструктуры"}],
                "confidence": "high",
                "needs_review": False,
            })
            resp = client.post(f"/api/documents/{doc_id}/recommend-architecture")
            assert resp.status_code == 200
            assert resp.json()["recommendation_json"]["recommended_pattern"] == "microservices"

    def test_generate_urs_not_found(self, client):
        resp = client.post("/api/documents/nonexistent-id/generate-urs")
        assert resp.status_code == 404

    def test_generate_srs_needs_review(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps({
                "content": "# SRS\nНеполные требования",
                "confidence": "low",
                "needs_review": True,
            })
            resp = client.post(f"/api/documents/{doc_id}/generate-srs")
            assert resp.status_code == 200
            assert resp.json()["needs_review"] is True
