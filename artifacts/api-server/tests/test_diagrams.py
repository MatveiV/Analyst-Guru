import json
from unittest.mock import patch


MOCK_DIAGRAMS = {
    "c4_context": "@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\nSystem(System1, \"Test System\")\n@enduml",
    "c4_container": "@startuml\nContainer(Web, \"Web App\")\n@enduml",
    "c4_component": "@startuml\nComponent(UI, \"UI Component\")\n@enduml",
    "use_case": "@startuml\n(UseCase1)\n@enduml",
    "sequence": "@startuml\nA -> B: message\n@enduml",
    "class_diagram": "@startuml\nclass Test {}\n@enduml",
    "erd": "@startuml\nentity Test {}\n@enduml",
    "mermaid_flowchart": "graph TD\nA[Start] --> B[End]",
    "confidence": "high",
    "needs_review": False,
}


class TestDiagrams:
    def _create_doc(self, client):
        resp = client.post("/api/documents", json={
            "title": "Test Doc for Diagrams",
            "text": "Тестовый документ для генерации диаграмм. Система должна поддерживать микросервисную архитектуру с API Gateway.",
            "doc_type": "tz",
        })
        return resp.json()["id"]

    def test_generate_diagrams(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps(MOCK_DIAGRAMS)
            resp = client.post(f"/api/documents/{doc_id}/generate-diagrams")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["diagrams"]) >= 1
            assert data["needs_review"] is False

    def test_generate_c4(self, client):
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps(MOCK_DIAGRAMS)
            resp = client.post("/api/diagrams/generate-c4", json={
                "text": "Система должна поддерживать микросервисную архитектуру с API Gateway.",
            })
            assert resp.status_code == 200
            assert len(resp.json()["diagrams"]) >= 1

    def test_generate_uml(self, client):
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps(MOCK_DIAGRAMS)
            resp = client.post("/api/diagrams/generate-uml", json={
                "text": "Система должна поддерживать асинхронное взаимодействие между сервисами.",
            })
            assert resp.status_code == 200
            assert len(resp.json()["diagrams"]) >= 1

    def test_generate_erd(self, client):
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps(MOCK_DIAGRAMS)
            resp = client.post("/api/diagrams/generate-erd", json={
                "text": "Система должна хранить данные пользователей, заказы и платежи.",
            })
            assert resp.status_code == 200
            assert len(resp.json()["diagrams"]) >= 1

    def test_get_diagram(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = json.dumps(MOCK_DIAGRAMS)
            gen_resp = client.post(f"/api/documents/{doc_id}/generate-diagrams")
            diagram_id = gen_resp.json()["diagrams"][0]["id"]
            resp = client.get(f"/api/diagrams/{diagram_id}")
            assert resp.status_code == 200
            assert resp.json()["id"] == diagram_id

    def test_get_diagram_not_found(self, client):
        resp = client.get("/api/diagrams/nonexistent-id")
        assert resp.status_code == 404

    def test_generate_diagrams_invalid_json(self, client):
        doc_id = self._create_doc(client)
        with patch("backend.services.ai_service.call_llm") as mock_call:
            mock_call.return_value = "not valid json"
            resp = client.post(f"/api/documents/{doc_id}/generate-diagrams")
            assert resp.status_code == 200
            data = resp.json()
            assert data["needs_review"] is True
            assert data["confidence"] == "low"
