import json
from unittest.mock import patch


class TestMemory:
    def test_store_memory(self, client):
        resp = client.post("/api/memory/store", json={
            "memory_type": "risk",
            "content": "Тестовый риск: возможна задержка поставки",
            "tags": ["risk", "delay"],
            "project_name": "TestProject",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["memory_type"] == "risk"
        assert data["tags"] == ["risk", "delay"]

    def test_search_memory(self, client):
        client.post("/api/memory/store", json={
            "memory_type": "lesson",
            "content": "Урок: всегда проверять совместимость версий",
        })
        resp = client.post("/api/memory/search", json={
            "query": "совместимость",
        })
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_search_memory_by_type(self, client):
        client.post("/api/memory/store", json={
            "memory_type": "decision",
            "content": "Решение: использовать FastAPI",
        })
        resp = client.post("/api/memory/search", json={
            "query": "FastAPI",
            "memory_type": "decision",
        })
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_recent_memory(self, client):
        resp = client.get("/api/memory/recent")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_recent_memory_filtered(self, client):
        resp = client.get("/api/memory/recent?memory_type=risk&limit=5")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_consolidate_memory(self, client):
        client.post("/api/memory/store", json={
            "memory_type": "risk",
            "content": "Дублирующийся риск",
        })
        client.post("/api/memory/store", json={
            "memory_type": "risk",
            "content": "Дублирующийся риск",
        })
        resp = client.post("/api/memory/consolidate")
        assert resp.status_code == 200
        assert resp.json()["deduplicated"] >= 1

    def test_store_memory_empty_content(self, client):
        resp = client.post("/api/memory/store", json={
            "memory_type": "risk",
            "content": "",
        })
        assert resp.status_code == 422
