from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ai_chat():
    response = client.post("/api/v1/ai/chat", json={"query": "What is AI?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
