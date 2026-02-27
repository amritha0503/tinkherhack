from sqlalchemy.orm import Session
from src.models.match import Match
from src.models.user import User
from src.models.skill import Skill
from src.repositories.match_repository import MatchRepository

class MatchService:
    def __init__(self, db: Session):
        self.db = db
        self.match_repository = MatchRepository(db)

    def create_match(self, user_id: int, skill_id: int) -> Match:
        match = Match(user_id=user_id, skill_id=skill_id)
        return self.match_repository.create(match)

    def get_matches_for_user(self, user_id: int) -> list[Match]:
        return self.match_repository.get_by_user_id(user_id)

    def get_matches_for_skill(self, skill_id: int) -> list[Match]:
        return self.match_repository.get_by_skill_id(skill_id)

    def delete_match(self, match_id: int) -> bool:
        return self.match_repository.delete(match_id)