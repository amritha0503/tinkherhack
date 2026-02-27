
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import Call, JobRequest
from auth import verify_token
from trust_score import calculate_trust_score
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

class InitiateCall(BaseModel):
    job_request_id: str

class EndCall(BaseModel):
    worker_responded: bool

class RateCall(BaseModel):
    rating: int
    review: Optional[str] = None

@router.post('/initiate')
def initiate_call(
    data: InitiateCall,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    job = db.query(JobRequest).filter(JobRequest.id == data.job_request_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    call = Call(
        id=str(uuid4()),
        job_request_id=job.id,
        customer_id=payload['sub'],
        worker_id=job.worker_id,
        call_start=datetime.utcnow()
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return {
        'call_id': call.id,
        'message': 'Call initiated — mock for demo',
        'note': 'In production: Exotel bridges customer and worker numbers'
    }

@router.put('/{call_id}/end')
def end_call(
    call_id: str,
    data: EndCall,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail='Call not found')
    call.call_end = datetime.utcnow()
    call.worker_responded = data.worker_responded
    if call.call_start:
        call.duration_seconds = int((call.call_end - call.call_start).total_seconds())
    db.commit()
    return {
        'duration_seconds': call.duration_seconds,
        'message': 'Call ended successfully'
    }

@router.put('/{call_id}/rating')
def rate_call(
    call_id: str,
    data: RateCall,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    call = db.query(Call).filter(Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail='Call not found')
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail='Rating must be between 1 and 5')
    call.post_call_rating = data.rating
    call.post_call_review = data.review
    db.commit()
    score = calculate_trust_score(call.worker_id, db)
    return {'rated': True, 'new_trust_score': score['total_score']}
