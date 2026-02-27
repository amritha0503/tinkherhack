from pydantic import BaseModel
from typing import List, Optional

class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int

    class Config:
        orm_mode = True

class SkillList(BaseModel):
    skills: List[Skill]