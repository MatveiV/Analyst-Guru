import json
import pytest


class TestDocuments:
    def test_create_document(self, client):
        resp = client.post("/api/documents", json={
            "title": "Test TZ",
            "text": "Нужна форма заявки для клиентов. Поля: имя, телефон, тип услуги.",
            "doc_type": "tz",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test TZ"
        assert data["id"] is not None
        assert data["is_kb"] is False

    def test_list_documents(self, client):
        client.post("/api/documents", json={
            "title": "Doc 1", "text": "Текст документа один. Должно быть больше десяти слов для валидации.",
        })
        client.post("/api/documents", json={
            "title": "Doc 2", "text": "Текст документа два. Должно быть больше десяти слов для валидации.",
        })
        resp = client.get("/api/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2

    def test_get_document(self, client):
        create_resp = client.post("/api/documents", json={
            "title": "Get Test", "text": "Тестовый документ для получения по идентификатору.",
        })
        doc_id = create_resp.json()["id"]
        resp = client.get(f"/api/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Get Test"

    def test_get_document_not_found(self, client):
        resp = client.get("/api/documents/nonexistent")
        assert resp.status_code == 404

    def test_delete_document(self, client):
        create_resp = client.post("/api/documents", json={
            "title": "Delete Test", "text": "Тестовый документ для удаления.",
        })
        doc_id = create_resp.json()["id"]
        resp = client.delete(f"/api/documents/{doc_id}")
        assert resp.status_code == 204
        resp = client.get(f"/api/documents/{doc_id}")
        assert resp.status_code == 404

    def test_create_document_validation(self, client):
        resp = client.post("/api/documents", json={"title": "", "text": "short"})
        assert resp.status_code == 422
