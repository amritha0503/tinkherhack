from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Worker, Customer
from auth import send_otp, verify_otp, create_token
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter()

class OTPRequest(BaseModel):
    phone: str
    role: str

class OTPVerify(BaseModel):
    phone: str
    otp: str
    role: str

@router.post('/send-otp')
def send_otp_endpoint(req: OTPRequest):
    send_otp(req.phone)
    return {
        'success': True,
        'message': f'OTP sent to {req.phone}'
    }

@router.post('/verify-otp')
def verify_otp_endpoint(req: OTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(req.phone, req.otp):
        raise HTTPException(status_code=400, detail='Invalid OTP')

    if req.role == 'worker':
        user = db.query(Worker).filter(Worker.phone == req.phone).first()
        if not user:
            user = Worker(id=str(uuid4()), phone=req.phone, name='')
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        user = db.query(Customer).filter(Customer.phone == req.phone).first()
        if not user:
            user = Customer(id=str(uuid4()), phone=req.phone, name='')
            db.add(user)
            db.commit()
            db.refresh(user)

    token = create_token(user.id, req.role)
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user_id': user.id,
        'role': req.role
    }