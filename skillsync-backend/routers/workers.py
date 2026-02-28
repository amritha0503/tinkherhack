from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import Worker, WorkerPhoto, WorkLedger
from auth import verify_token
from trust_score import calculate_trust_score
from distance import haversine
from ai import voice_to_text, extract_profile
from pydantic import BaseModel
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
import shutil
import os

router = APIRouter()
security = HTTPBearer()

class WorkerRegister(BaseModel):
    name: str
    language: str = 'hi'
    skill_type: Optional[str] = None
    experience_years: Optional[int] = None
    daily_rate: Optional[float] = None
    work_radius_km: int = 10
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_area: Optional[str] = None

class AadhaarVerify(BaseModel):
    worker_id: str
    aadhaar_last4: str

class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    skill_type: Optional[str] = None
    experience_years: Optional[int] = None
    daily_rate: Optional[float] = None
    work_radius_km: Optional[int] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_area: Optional[str] = None

@router.post('/register')
def register_worker(
    data: WorkerRegister,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    worker = db.query(Worker).filter(Worker.id == payload['sub']).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found. Please verify OTP first.')
    for key, value in data.dict(exclude_none=True).items():
        setattr(worker, key, value)
    # Mark profile complete if essential fields are present
    if all([worker.name, worker.skill_type, worker.location_lat, worker.daily_rate]):
        worker.profile_complete = True
    db.commit()
    db.refresh(worker)
    score = calculate_trust_score(worker.id, db)
    return {
        'worker_id': worker.id,
        'trust_score': score['total_score'],
        'profile_complete': worker.profile_complete,
        'message': 'Profile created successfully'
    }

@router.post('/aadhaar-verify')
def aadhaar_verify(
    data: AadhaarVerify,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')
    worker.aadhaar_last4 = data.aadhaar_last4
    worker.aadhaar_verified = True
    db.commit()
    score = calculate_trust_score(worker.id, db)
    return {'verified': True, 'new_trust_score': score['total_score']}

@router.post('/{worker_id}/voice-bio')
async def upload_voice_bio(
    worker_id: str,
    audio: UploadFile = File(...),
    language: str = Form('hi'),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')

    os.makedirs('uploads/audio', exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f'{worker_id}_{timestamp}.mp3'
    filepath = f'uploads/audio/{filename}'

    with open(filepath, 'wb') as f:
        shutil.copyfileobj(audio.file, f)

    try:
        transcript = voice_to_text(filepath, language)
        profile = extract_profile(transcript, language)
        worker.skill_type = profile.get('skill_type') or worker.skill_type
        worker.experience_years = profile.get('experience_years') or worker.experience_years
        worker.daily_rate = profile.get('daily_rate') or worker.daily_rate
        worker.bio_text = profile.get('bio_english') or worker.bio_text
        specializations = profile.get('specializations', [])
        if specializations:
            worker.sub_skills = ','.join(specializations)
        worker.voice_bio_path = filepath
        db.commit()
        score = calculate_trust_score(worker.id, db)
        return {
            'transcript': transcript,
            'extracted_profile': profile,
            'new_trust_score': score['total_score']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'AI processing failed: {str(e)}')

@router.post('/{worker_id}/photos')
async def upload_photos(
    worker_id: str,
    photos: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')

    os.makedirs('uploads/photos', exist_ok=True)
    photo_ids = []
    for photo in photos[:10]:
        ext = photo.filename.split('.')[-1] if '.' in photo.filename else 'jpg'
        filename = f'{worker_id}_{uuid4()}.{ext}'
        filepath = f'uploads/photos/{filename}'
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(photo.file, f)
        wp = WorkerPhoto(
            id=str(uuid4()),
            worker_id=worker_id,
            file_path=filepath
        )
        db.add(wp)
        photo_ids.append(wp.id)
    db.commit()
    return {'uploaded': len(photo_ids), 'photo_ids': photo_ids}

@router.get('/search')
def search_workers(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    skill: Optional[str] = None,
    skill_type: Optional[str] = None,
    location: Optional[str] = None,
    radius_km: int = 50,
    min_trust: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    # Accept skill_type as alias for skill
    skill = skill or skill_type

    query = db.query(Worker).filter(
        Worker.account_status == 'active',
        Worker.trust_score >= min_trust
    )
    if skill:
        query = query.filter(Worker.skill_type == skill)
    if location:
        query = query.filter(Worker.location_area.ilike(f'%{location}%'))
    all_workers = query.all()

    # If no coordinates provided, return all matching workers without distance
    if lat is None or lng is None:
        results = []
        for w in all_workers:
            ledger = db.query(WorkLedger).filter(WorkLedger.worker_id == w.id).all()
            avg_rating = round(sum(e.rating for e in ledger) / len(ledger), 1) if ledger else 0.0
            results.append({
                'id': w.id,
                'name': w.name,
                'skill_type': w.skill_type,
                'trust_score': w.trust_score,
                'trust_badge': w.trust_badge,
                'distance_km': None,
                'daily_rate': w.daily_rate,
                'experience_years': w.experience_years,
                'location_area': w.location_area,
                'avg_rating': avg_rating,
                'verified_jobs': len(ledger),
                'bio_text': w.bio_text,
                'aadhaar_verified': w.aadhaar_verified,
            })
        results.sort(key=lambda x: -(x['trust_score'] or 0))
        return {'workers': results[:limit], 'total': len(results)}

    results = []
    for w in all_workers:
        if w.location_lat is not None and w.location_lng is not None:
            dist = haversine(lat, lng, w.location_lat, w.location_lng)
            if dist <= radius_km:
                ledger = db.query(WorkLedger).filter(WorkLedger.worker_id == w.id).all()
                avg_rating = round(sum(e.rating for e in ledger) / len(ledger), 1) if ledger else 0.0
                results.append({
                    'id': w.id,
                    'name': w.name,
                    'skill_type': w.skill_type,
                    'trust_score': w.trust_score,
                    'trust_badge': w.trust_badge,
                    'distance_km': round(dist, 2),
                    'daily_rate': w.daily_rate,
                    'experience_years': w.experience_years,
                    'location_area': w.location_area,
                    'avg_rating': avg_rating,
                    'verified_jobs': len(ledger),
                    'bio_text': w.bio_text,
                    'aadhaar_verified': w.aadhaar_verified,
                })
    results.sort(key=lambda x: x['distance_km'])
    return {'workers': results[:limit], 'total': len(results)}

@router.get('/{worker_id}/trust-score')
def get_trust_score(
    worker_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    verify_token(credentials.credentials)
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')
    return calculate_trust_score(worker_id, db)

@router.get('/{worker_id}/ledger')
def get_ledger(worker_id: str, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')
    entries = db.query(WorkLedger).filter(
        WorkLedger.worker_id == worker_id
    ).order_by(WorkLedger.created_at.desc()).all()
    return {
        'entries': [{
            'job_type': e.job_type,
            'rating': e.rating,
            'review_text': e.review_text,
            'completed_date': str(e.completed_date),
            'location_area': e.location_area,
            'verified': e.verified
        } for e in entries],
        'total': len(entries)
    }

@router.get('/{worker_id}')
def get_worker(worker_id: str, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')
    photos = db.query(WorkerPhoto).filter(WorkerPhoto.worker_id == worker_id).all()
    reviews = db.query(WorkLedger).filter(
        WorkLedger.worker_id == worker_id
    ).order_by(WorkLedger.created_at.desc()).limit(5).all()
    return {
        'id': worker.id,
        'name': worker.name,
        'phone': worker.phone,
        'skill_type': worker.skill_type,
        'sub_skills': worker.sub_skills,
        'experience_years': worker.experience_years,
        'daily_rate': worker.daily_rate,
        'work_radius_km': worker.work_radius_km,
        'trust_score': worker.trust_score,
        'trust_badge': worker.trust_badge,
        'bio_text': worker.bio_text,
        'location_area': worker.location_area,
        'location_lat': worker.location_lat,
        'location_lng': worker.location_lng,
        'aadhaar_verified': worker.aadhaar_verified,
        'account_status': worker.account_status,
        'profile_complete': worker.profile_complete,
        'created_at': str(worker.created_at),
        'photos': [{'id': p.id, 'file_path': p.file_path} for p in photos],
        'reviews': [{
            'rating': r.rating,
            'review_text': r.review_text,
            'job_type': r.job_type,
            'completed_date': str(r.completed_date)
        } for r in reviews]
    }

@router.put('/{worker_id}')
def update_worker(
    worker_id: str,
    data: WorkerUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail='Worker not found')
    for key, value in data.dict(exclude_none=True).items():
        setattr(worker, key, value)
    db.commit()
    score = calculate_trust_score(worker.id, db)
    return {'updated': True, 'new_trust_score': score['total_score']}
