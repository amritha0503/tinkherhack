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

LANGUAGE_MAP = {
    '1': 'hi', '2': 'ta', '3': 'te',
    '4': 'kn', '5': 'ml', '6': 'bn',
    '7': 'mr', '8': 'en'
}
SKILL_MAP = {
    '1': 'Plumber', '2': 'Electrician',
    '3': 'Carpenter', '4': 'Mason', '5': 'Painter'
}

class IVRStart(BaseModel):
    phone: str

class IVRRespond(BaseModel):
    session_id: str
    digit: Optional[str] = None
    voice_text: Optional[str] = None

@router.post('/start')
def ivr_start(data: IVRStart, db: Session = Depends(get_db)):
    session = IVRSession(
        id=str(uuid4()),
        phone=data.phone,
        current_state='LANGUAGE_SELECT',
        collected_data='{}',
        completed=False
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        'session_id': session.id,
        'current_state': 'LANGUAGE_SELECT',
        'prompt': 'Welcome to SkillSync. Please select your language:',
        'options': {
            '1': 'Hindi', '2': 'Tamil', '3': 'Telugu',
            '4': 'Kannada', '5': 'Malayalam', '6': 'Bengali',
            '7': 'Marathi', '8': 'English'
        }
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

    if state == 'LANGUAGE_SELECT':
        if data.digit in LANGUAGE_MAP:
            session.language = LANGUAGE_MAP[data.digit]
            collected['language'] = session.language
            session.current_state = 'NAME'
            prompt = 'Please tell us your full name'
        else:
            prompt = 'Invalid choice. Press 1-Hindi 2-Tamil 3-Telugu 4-Kannada 5-Malayalam 6-Bengali 7-Marathi 8-English'

    elif state == 'NAME':
        if data.voice_text:
            collected['name'] = data.voice_text
            session.current_state = 'AADHAAR'
            prompt = 'Please enter the last 4 digits of your Aadhaar number'
        else:
            prompt = 'Please say your full name'

    elif state == 'AADHAAR':
        if data.digit and len(data.digit) == 4 and data.digit.isdigit():
            collected['aadhaar_last4'] = data.digit
            session.current_state = 'OTP_VERIFY'
            send_otp(session.phone)
            prompt = 'OTP has been sent to your number. Please enter the 6-digit OTP'
        else:
            prompt = 'Please enter exactly 4 digits of your Aadhaar'

    elif state == 'OTP_VERIFY':
        if verify_otp(session.phone, data.digit):
            session.current_state = 'SKILL'
            prompt = 'Please select your skill: 1-Plumber 2-Electrician 3-Carpenter 4-Mason 5-Painter'
            options = SKILL_MAP
        else:
            prompt = 'Invalid OTP. Please enter the 6-digit OTP sent to your number'

    elif state == 'SKILL':
        if data.digit in SKILL_MAP:
            collected['skill_type'] = SKILL_MAP[data.digit]
            session.current_state = 'EXPERIENCE'
            prompt = 'How many years of experience do you have? Please enter the number'
        else:
            prompt = 'Invalid choice. Press 1-Plumber 2-Electrician 3-Carpenter 4-Mason 5-Painter'
            options = SKILL_MAP

    elif state == 'EXPERIENCE':
        if data.digit and data.digit.isdigit():
            collected['experience_years'] = int(data.digit)
            session.current_state = 'LOCATION'
            prompt = 'Which area do you work in? Please say your area name'
        else:
            prompt = 'Please enter a valid number of years'

    elif state == 'LOCATION':
        if data.voice_text:
            collected['location_area'] = data.voice_text
            session.current_state = 'RATE'
            prompt = 'What is your daily rate in rupees? Please enter the amount'
        else:
            prompt = 'Please say your work area name'

    elif state == 'RATE':
        if data.digit and data.digit.isdigit():
            collected['daily_rate'] = float(data.digit)
            session.current_state = 'CONFIRM'
            prompt = (
                f"Here is your profile summary: "
                f"Name: {collected.get('name', 'N/A')}, "
                f"Skill: {collected.get('skill_type', 'N/A')}, "
                f"Experience: {collected.get('experience_years', 0)} years, "
                f"Daily Rate: Rs.{collected.get('daily_rate', 0)}. "
                f"Press 1 to confirm and create your profile."
            )
        else:
            prompt = 'Please enter a valid amount in rupees'

    elif state == 'CONFIRM':
        if data.digit == '1':
            # Check if phone already registered
            existing = db.query(Worker).filter(Worker.phone == session.phone).first()
            if existing:
                worker_id = existing.id
                completed = True
                session.completed = True
                prompt = 'Your profile already exists! It has been updated.'
            else:
                worker = Worker(
                    id=str(uuid4()),
                    phone=session.phone,
                    name=collected.get('name', ''),
                    skill_type=collected.get('skill_type'),
                    experience_years=collected.get('experience_years'),
                    daily_rate=collected.get('daily_rate'),
                    location_area=collected.get('location_area'),
                    aadhaar_last4=collected.get('aadhaar_last4'),
                    aadhaar_verified=False,
                    language=session.language or 'hi',
                    trust_score=0,
                    trust_badge='Red',
                    account_status='active'
                )
                db.add(worker)
                db.flush()
                worker_id = worker.id
                completed = True
                session.completed = True
                prompt = 'Profile created successfully! You will receive a WhatsApp message with your profile link shortly.'
        else:
            prompt = 'Press 1 to confirm your profile, or restart by calling again.'

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
