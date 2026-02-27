from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gemini_service import GeminiService

router = APIRouter()
gemini_service = GeminiService()

class AIRequest(BaseModel):
    query: str

class AIResponse(BaseModel):
    response: str

@router.post("/ai/query", response_model=AIResponse)
async def query_ai(ai_request: AIRequest):
    try:
        response = await gemini_service.get_response(ai_request.query)
        return AIResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))