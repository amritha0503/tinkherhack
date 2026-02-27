from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_gemini_endpoint():
    response = client.post("/ai/gemini", json={"input": "test input"})
    assert response.status_code == 200
    assert "output" in response.json()

def test_gemini_invalid_input():
    response = client.post("/ai/gemini", json={"input": ""})
    assert response.status_code == 400
    assert "detail" in response.json()