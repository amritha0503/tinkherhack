from pydantic import BaseModel
from typing import List, Optional

class MatchBase(BaseModel):
    user_id: int
    skill_id: int

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int

    class Config:
        orm_mode = True

class MatchResponse(BaseModel):
    matches: List[Match]