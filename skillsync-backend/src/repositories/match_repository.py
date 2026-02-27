from sqlalchemy.orm import Session
from models.match import Match
from schemas.match import MatchCreate, MatchUpdate

class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_match(self, match: MatchCreate) -> Match:
        db_match = Match(**match.dict())
        self.db.add(db_match)
        self.db.commit()
        self.db.refresh(db_match)
        return db_match

    def get_match(self, match_id: int) -> Match:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def update_match(self, match_id: int, match: MatchUpdate) -> Match:
        db_match = self.get_match(match_id)
        if db_match:
            for key, value in match.dict(exclude_unset=True).items():
                setattr(db_match, key, value)
            self.db.commit()
            self.db.refresh(db_match)
        return db_match

    def delete_match(self, match_id: int) -> bool:
        db_match = self.get_match(match_id)
        if db_match:
            self.db.delete(db_match)
            self.db.commit()
            return True
        return False

    def get_all_matches(self):
        return self.db.query(Match).all()