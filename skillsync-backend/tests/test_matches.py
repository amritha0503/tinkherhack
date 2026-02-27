from fastapi.testclient import TestClient
from src.main import app
from src.models.match import Match
from src.repositories.match_repository import MatchRepository

client = TestClient(app)

def test_create_match():
    response = client.post("/matches/", json={"user_id": 1, "skill_id": 1})
    assert response.status_code == 201
    assert response.json() == {"user_id": 1, "skill_id": 1}

def test_get_match():
    response = client.get("/matches/1")
    assert response.status_code == 200
    assert response.json() == {"user_id": 1, "skill_id": 1}

def test_get_all_matches():
    response = client.get("/matches/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_match():
    response = client.delete("/matches/1")
    assert response.status_code == 204
    assert response.content == b""