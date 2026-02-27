from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import JobRequest, QRCode, Customer
from auth import verify_token
from ai import analyze_complaint_photo
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
import shutil
import os

router = APIRouter()
security = HTTPBearer()

class JobRespond(BaseModel):
    response: str  # 'accepted' or 'declined'
    message: Optional[str] = None

class JobDispute(BaseModel):
    reason: str

@router.post('')
async def create_job(
    worker_id: str = Form(...),
    complaint_description: Optional[str] = Form(None),
    complaint_photo: Optional[UploadFile] = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    customer_id = payload['sub']

    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail='Customer not found. Please register first.')

    job = JobRequest(
        id=str(uuid4()),
        customer_id=customer_id,
        worker_id=worker_id,
        complaint_description=complaint_description,
        job_status='pending'
    )

    ai_analysis = {}
    if complaint_photo:
        try:
            os.makedirs('uploads/photos', exist_ok=True)
            ext = complaint_photo.filename.split('.')[-1] if '.' in complaint_photo.filename else 'jpg'
            filename = f'complaint_{uuid4()}.{ext}'
            filepath = f'uploads/photos/{filename}'
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(complaint_photo.file, f)
            job.complaint_photo_path = filepath
            ai_result = analyze_complaint_photo(filepath)
            job.ai_issue_type = ai_result.get('issue_type')
            job.ai_description = ai_result.get('description_for_worker')
            ai_analysis = ai_result
        except Exception as e:
            ai_analysis = {'error': str(e)}

    db.add(job)
    db.commit()
    db.refresh(job)
    return {
        'request_id': job.id,
        'status': 'pending',
        'ai_analysis': ai_analysis
    }

@router.get('/worker/{worker_id}')
def get_worker_jobs(
    worker_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    jobs = db.query(JobRequest).filter(
        JobRequest.worker_id == worker_id,
        JobRequest.job_status == 'pending'
    ).all()
    return {
        'jobs': [{
            'id': j.id,
            'customer_id': j.customer_id,
            'status': j.job_status,
            'description': j.complaint_description,
            'ai_issue': j.ai_issue_type,
            'ai_description': j.ai_description,
            'created_at': str(j.created_at)
        } for j in jobs]
    }

@router.get('/{request_id}')
def get_job(
    request_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    job = db.query(JobRequest).filter(JobRequest.id == request_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return {
        'id': job.id,
        'customer_id': job.customer_id,
        'worker_id': job.worker_id,
        'complaint_description': job.complaint_description,
        'complaint_photo_path': job.complaint_photo_path,
        'ai_issue_type': job.ai_issue_type,
        'ai_description': job.ai_description,
        'job_status': job.job_status,
        'worker_response': job.worker_response,
        'created_at': str(job.created_at),
        'completed_at': str(job.completed_at) if job.completed_at else None
    }

@router.put('/{request_id}/respond')
def respond_to_job(
    request_id: str,
    data: JobRespond,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    job = db.query(JobRequest).filter(JobRequest.id == request_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    if data.response not in ['accepted', 'declined']:
        raise HTTPException(status_code=400, detail="response must be 'accepted' or 'declined'")
    job.job_status = 'accepted' if data.response == 'accepted' else 'cancelled'
    job.worker_response = data.response
    db.commit()
    return {'status': 'updated', 'job_status': job.job_status}

@router.put('/{request_id}/complete')
def complete_job(
    request_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    job = db.query(JobRequest).filter(JobRequest.id == request_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    job.job_status = 'completed'
    job.completed_at = datetime.utcnow()
    qr = QRCode(
        id=str(uuid4()),
        worker_id=job.worker_id,
        job_request_id=job.id,
        issued_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(qr)
    db.commit()
    return {
        'qr_id': qr.id,
        'expires_at': str(qr.expires_at),
        'message': 'Show this QR to customer to collect review'
    }

@router.put('/{request_id}/dispute')
def dispute_job(
    request_id: str,
    data: JobDispute,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    job = db.query(JobRequest).filter(JobRequest.id == request_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    job.job_status = 'disputed'
    job.dispute_reason = data.reason
    db.commit()
    return {'status': 'disputed', 'message': 'Dispute logged successfully'}
