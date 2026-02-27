from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.models.user import User
from src.repositories.user_repository import UserRepository

app = FastAPI()
client = TestClient(app)

@app.post("/users/", response_model=User)
def create_user(user: User):
    return UserRepository.create(user)

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
    return UserRepository.get(user_id)

def test_create_user():
    response = client.post("/users/", json={"name": "Test User", "email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test User"

def test_read_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1