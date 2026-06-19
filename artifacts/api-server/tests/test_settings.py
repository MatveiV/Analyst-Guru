import json
from unittest.mock import patch


class TestSettings:
    def test_get_ai_setting_default(self, client):
        resp = client.get("/api/settings/ai")
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openrouter"
        assert data["has_api_key"] is False
        assert data["base_url"] == "https://openrouter.ai/api/v1"
        assert data["model"] == "openrouter/free"
        assert data["max_tokens"] == 4096
        assert data["temperature"] == 0.2

    def test_update_ai_setting(self, client):
        resp = client.put("/api/settings/ai", json={
            "provider": "openai",
            "api_key": "sk-test123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openai"
        assert data["has_api_key"] is True
        assert data["model"] == "gpt-4o"

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
        assert resp.json()["model"] == "gpt-4o-mini"

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

    def test_update_ai_setting_with_all_fields(self, client):
        resp = client.put("/api/settings/ai", json={
            "provider": "openrouter",
            "api_key": "or-key",
            "base_url": "https://custom.openrouter.ai/v1",
            "model": "anthropic/claude-3.5-sonnet",
            "max_tokens": 8192,
            "temperature": 0.5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "openrouter"
        assert data["has_api_key"] is True
        assert data["base_url"] == "https://custom.openrouter.ai/v1"
        assert data["model"] == "anthropic/claude-3.5-sonnet"
        assert data["max_tokens"] == 8192
        assert data["temperature"] == 0.5

    def test_update_ai_setting_partial_update(self, client):
        client.put("/api/settings/ai", json={
            "provider": "openai",
            "api_key": "sk-first",
            "model": "gpt-4-turbo",
        })
        resp = client.put("/api/settings/ai", json={
            "provider": "openai",
            "temperature": 0.7,
        })
        data = resp.json()
        assert data["model"] == "gpt-4-turbo"
        assert data["temperature"] == 0.7
        assert data["has_api_key"] is True
