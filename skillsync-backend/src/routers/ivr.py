from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import IVRSession, Worker
from auth import verify_otp, send_otp
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime
import json

router = APIRouter()

LANGUAGE_MAP = {'1': 'hi', '2': 'ta', '3': 'te', '4': 'kn', '5': 'ml', '6': 'bn', '7': 'mr', '8': 'en'}
SKILL_MAP = {'1': 'Plumber', '2': 'Electrician', '3': 'Carpenter', '4': 'Mason', '5': 'Painter'}

class IVRStart(BaseModel):
    phone: str

class IVRRespond(BaseModel):
    session_id: str
    digit: Optional[str] = None
    voice_text: Optional[str] = None

@router.post('/start')
def ivr_start(data: IVRStart, db: Session = Depends(get_db)):
    session = IVRSession(id=str(uuid4()), phone=data.phone, collected_data='{}')
    db.add(session)
    db.commit()
    return {
        'session_id': session.id,
        'current_state': 'LANGUAGE_SELECT',
        'prompt': 'Welcome to SkillSync. Please select your language:',
        'options': {'1': 'Hindi', '2': 'Tamil', '3': 'Telugu', '4': 'Kannada',
                    '5': 'Malayalam', '6': 'Bengali', '7': 'Marathi', '8': 'English'}
    }

@router.post('/respond')
def ivr_respond(data: IVRRespond, db: Session = Depends(get_db)):
    session = db.query(IVRSession).filter(IVRSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail='IVR session not found')
    if session.completed:
        raise HTTPException(status_code=400, detail='Session already completed')
    collected = json.loads(session.collected_data or '{}')
    state = session.current_state
    prompt = 'Invalid input. Please try again.'
    options = None
    completed = False
    worker_id = None

    if state == 'LANGUAGE_SELECT' and data.digit in LANGUAGE_MAP:
        session.language = LANGUAGE_MAP[data.digit]
        collected['language'] = session.language
        session.current_state = 'NAME'
        prompt = 'Please tell us your full name'

    elif state == 'NAME' and data.voice_text:
        collected['name'] = data.voice_text
        session.current_state = 'AADHAAR'
        prompt = 'Enter last 4 digits of Aadhaar'

    elif state == 'AADHAAR' and data.digit:
        collected['aadhaar_last4'] = data.digit
        session.current_state = 'OTP_VERIFY'
        send_otp(session.phone)
        prompt = 'OTP sent to your number. Enter 6-digit OTP'

    elif state == 'OTP_VERIFY' and verify_otp(session.phone, data.digit):
        session.current_state = 'SKILL'
        prompt = 'Select skill: 1-Plumber 2-Electrician 3-Carpenter 4-Mason 5-Painter'
        options = SKILL_MAP

    elif state == 'SKILL' and data.digit in SKILL_MAP:
        collected['skill_type'] = SKILL_MAP[data.digit]
        session.current_state = 'EXPERIENCE'
        prompt = 'How many years of experience do you have?'

    elif state == 'EXPERIENCE' and data.digit:
        collected['experience_years'] = int(data.digit)
        session.current_state = 'LOCATION'
        prompt = 'Which area do you work in?'

    elif state == 'LOCATION' and data.voice_text:
        collected['location_area'] = data.voice_text
        session.current_state = 'RATE'
        prompt = 'What is your daily rate in rupees?'

    elif state == 'RATE' and data.digit:
        collected['daily_rate'] = float(data.digit)
        session.current_state = 'CONFIRM'
        prompt = (f"Summary: Name={collected.get('name')}, Skill={collected.get('skill_type')}, "
                  f"Exp={collected.get('experience_years')}yrs, Rate=₹{collected.get('daily_rate')}/day. Press 1 to confirm")

    elif state == 'CONFIRM' and data.digit == '1':
        worker = Worker(
            id=str(uuid4()),
            phone=session.phone,
            name=collected.get('name', ''),
            skill_type=collected.get('skill_type'),
            experience_years=collected.get('experience_years'),
            daily_rate=collected.get('daily_rate'),
            location_area=collected.get('location_area'),
            aadhaar_last4=collected.get('aadhaar_last4'),
            language=session.language or 'hi'
        )
        db.add(worker)
        session.completed = True
        worker_id = worker.id
        completed = True
        prompt = 'Profile created! You will receive a WhatsApp with your profile link.'

    session.collected_data = json.dumps(collected)
    session.updated_at = datetime.utcnow()
    db.commit()

    return {
        'session_id': session.id,
        'current_state': session.current_state,
        'prompt': prompt,
        'options': options,
        'completed': completed,
        'worker_id': worker_id
    }