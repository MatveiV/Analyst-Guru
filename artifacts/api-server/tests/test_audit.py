class TestAudit:
    def test_list_audit(self, client):
        resp = client.get("/api/audit")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_audit_with_filters(self, client):
        resp = client.get("/api/audit?action=review&status=ok")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_audit_pagination(self, client):
        resp = client.get("/api/audit?limit=5&offset=0")
        assert resp.status_code == 200
        assert len(resp.json()) <= 5
