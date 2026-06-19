import json
from unittest.mock import patch


class TestSettings:
    def test_get_ai_setting_default(self, client):
        resp = client.get("/api/settings/ai")
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openrouter"
        assert data["has_api_key"] is False

    def test_update_ai_setting(self, client):
        resp = client.put("/api/settings/ai", json={
            "provider": "openai",
            "api_key": "sk-test123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openai"
        assert data["has_api_key"] is True

    def test_update_ai_setting_invalid_provider(self, client):
        resp = client.put("/api/settings/ai", json={
            "provider": "invalid_provider",
        })
        assert resp.status_code == 400

    def test_update_ai_setting_persists(self, client):
        client.put("/api/settings/ai", json={
            "provider": "proxyapi",
            "api_key": "pk-test456",
        })
        resp = client.get("/api/settings/ai")
        assert resp.json()["provider"] == "proxyapi"
        assert resp.json()["has_api_key"] is True

    def test_update_ai_setting_no_key_clear(self, client):
        client.put("/api/settings/ai", json={
            "provider": "anthropic",
            "api_key": "sk-old",
        })
        client.put("/api/settings/ai", json={
            "provider": "anthropic",
        })
        resp = client.get("/api/settings/ai")
        assert resp.json()["has_api_key"] is True
