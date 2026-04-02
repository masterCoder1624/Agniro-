from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_career_analysis():
    response = client.post("/api/v1/careers/analyze", json={
        "skills": ["Python", "SQL"],
        "target_career": "Data Scientist"
    })
    assert response.status_code == 200
    data = response.json()
    assert "missing_skills" in data
    assert "recommended_resources" in data
