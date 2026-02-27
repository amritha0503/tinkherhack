from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import QRCode, JobRequest, Worker, WorkLedger
from auth import verify_token
from trust_score import calculate_trust_score
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime, date

router = APIRouter()
security = HTTPBearer()

class ScanQR(BaseModel):
    qr_id: str

class SubmitReview(BaseModel):
    qr_id: str
    rating: int
    review_text: Optional[str] = None

@router.post('/scan-qr')
def scan_qr(
    data: ScanQR,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    qr = db.query(QRCode).filter(QRCode.id == data.qr_id).first()
    if not qr:
        raise HTTPException(status_code=404, detail='QR not found')
    if qr.used:
        raise HTTPException(status_code=400, detail='QR already used')
    if qr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail='QR expired')
    job = db.query(JobRequest).filter(JobRequest.id == qr.job_request_id).first()
    worker = db.query(Worker).filter(Worker.id == qr.worker_id).first()
    return {
        'valid': True,
        'job_type': job.ai_issue_type,
        'worker_name': worker.name,
        'worker_skill': worker.skill_type,
        'completed_date': str(job.completed_at)
    }

@router.post('/submit')
def submit_review(
    data: SubmitReview,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    qr = db.query(QRCode).filter(QRCode.id == data.qr_id).first()
    if not qr or qr.used or qr.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail='Invalid or expired QR')
    job = db.query(JobRequest).filter(JobRequest.id == qr.job_request_id).first()
    worker = db.query(Worker).filter(Worker.id == qr.worker_id).first()
    entry = WorkLedger(
        id=str(uuid4()),
        worker_id=qr.worker_id,
        customer_id=payload['sub'],
        job_request_id=qr.job_request_id,
        job_type=worker.skill_type or 'General',
        rating=data.rating,
        review_text=data.review_text,
        completed_date=date.today(),
        location_area=worker.location_area,
        verified=True
    )
    db.add(entry)
    qr.used = True
    qr.used_at = datetime.utcnow()
    job.job_status = 'completed'
    db.commit()
    score = calculate_trust_score(qr.worker_id, db)
    return {'success': True, 'ledger_entry_id': entry.id, 'new_trust_score': score['total_score'], 'new_badge': score['badge']}