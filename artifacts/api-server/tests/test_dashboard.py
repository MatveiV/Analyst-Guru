class TestDashboard:
    def test_get_stats(self, client):
        resp = client.get("/api/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_documents" in data
        assert "total_reviews" in data
        assert "total_kb_documents" in data
        assert "total_qa_runs" in data
        assert "needs_review_count" in data
        assert "total_audit_runs" in data
        assert "error_count" in data
        assert "avg_duration_ms" in data

    def test_recent_activity(self, client):
        resp = client.get("/api/dashboard/recent-activity")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_health_check(self, client):
        resp = client.get("/api/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
