from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.match import MatchCreate, MatchResponse
from src.services.match_service import MatchService

router = APIRouter()
match_service = MatchService()

@router.post("/matches/", response_model=MatchResponse)
async def create_match(match: MatchCreate):
    created_match = await match_service.create_match(match)
    if not created_match:
        raise HTTPException(status_code=400, detail="Match could not be created")
    return created_match

@router.get("/matches/", response_model=List[MatchResponse])
async def get_matches():
    return await match_service.get_all_matches()

@router.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int):
    match = await match_service.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.delete("/matches/{match_id}", response_model=dict)
async def delete_match(match_id: int):
    success = await match_service.delete_match(match_id)
    if not success:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"detail": "Match deleted successfully"}