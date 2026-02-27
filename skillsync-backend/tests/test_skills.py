from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.models.skill import Skill
from src.schemas.skill import SkillCreate
from src.database import SessionLocal, engine
from src.repositories.skill_repository import SkillRepository

app = FastAPI()
client = TestClient(app)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/skills/", response_model=Skill)
def create_skill(skill: SkillCreate, db: Session = next(get_db())):
    skill_repo = SkillRepository(db)
    return skill_repo.create(skill)

def test_create_skill():
    response = client.post("/skills/", json={"name": "Python", "description": "A programming language"})
    assert response.status_code == 200
    assert response.json()["name"] == "Python"
    assert response.json()["description"] == "A programming language"

def test_get_skills():
    response = client.get("/skills/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Ensure the response is a list

def test_update_skill():
    # Assuming a skill with id 1 exists
    response = client.put("/skills/1", json={"name": "Python Updated", "description": "Updated description"})
    assert response.status_code == 200
    assert response.json()["name"] == "Python Updated"

def test_delete_skill():
    # Assuming a skill with id 1 exists
    response = client.delete("/skills/1")
    assert response.status_code == 204  # No content on successful delete

# Additional tests can be added as needed.