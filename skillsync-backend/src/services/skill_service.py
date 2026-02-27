from sqlalchemy.orm import Session
from src.models.skill import Skill
from src.schemas.skill import SkillCreate, SkillUpdate

class SkillService:
    def __init__(self, db: Session):
        self.db = db

    def create_skill(self, skill: SkillCreate) -> Skill:
        db_skill = Skill(**skill.dict())
        self.db.add(db_skill)
        self.db.commit()
        self.db.refresh(db_skill)
        return db_skill

    def get_skill(self, skill_id: int) -> Skill:
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def update_skill(self, skill_id: int, skill: SkillUpdate) -> Skill:
        db_skill = self.get_skill(skill_id)
        if db_skill:
            for key, value in skill.dict(exclude_unset=True).items():
                setattr(db_skill, key, value)
            self.db.commit()
            self.db.refresh(db_skill)
        return db_skill

    def delete_skill(self, skill_id: int) -> bool:
        db_skill = self.get_skill(skill_id)
        if db_skill:
            self.db.delete(db_skill)
            self.db.commit()
            return True
        return False

    def get_all_skills(self):
        return self.db.query(Skill).all()