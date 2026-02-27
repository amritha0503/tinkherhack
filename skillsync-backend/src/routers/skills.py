from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.skill import SkillCreate, SkillResponse
from src.services.skill_service import SkillService

router = APIRouter()
skill_service = SkillService()

@router.post("/skills/", response_model=SkillResponse)
async def create_skill(skill: SkillCreate):
    return await skill_service.create_skill(skill)

@router.get("/skills/", response_model=List[SkillResponse])
async def get_skills():
    return await skill_service.get_all_skills()

@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int):
    skill = await skill_service.get_skill_by_id(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: int, skill: SkillCreate):
    updated_skill = await skill_service.update_skill(skill_id, skill)
    if not updated_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated_skill

@router.delete("/skills/{skill_id}", response_model=dict)
async def delete_skill(skill_id: int):
    success = await skill_service.delete_skill(skill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"message": "Skill deleted successfully"}