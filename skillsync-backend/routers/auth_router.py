from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Worker, Customer
from auth import send_otp, verify_otp, create_token, hash_password, verify_password
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter()

class OTPRequest(BaseModel):
    phone: str
    role: str  # 'worker' or 'customer'

class OTPVerify(BaseModel):
    phone: str
    otp: str
    role: str

@router.post('/send-otp')
def send_otp_endpoint(req: OTPRequest):
    if req.role not in ['worker', 'customer']:
        raise HTTPException(status_code=400, detail="role must be 'worker' or 'customer'")
    send_otp(req.phone)
    return {
        'success': True,
        'message': f'OTP sent to {req.phone}'
    }

class CustomerRegister(BaseModel):
    name: str
    email: str
    password: str

class CustomerLogin(BaseModel):
    email: str
    password: str

@router.post('/customer/register')
def customer_register(req: CustomerRegister, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == req.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')
    customer = Customer(
        id=str(uuid4()),
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password)
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    token = create_token(customer.id, 'customer')
    return {'access_token': token, 'token_type': 'bearer', 'user_id': customer.id, 'name': customer.name, 'email': customer.email}

@router.post('/customer/login')
def customer_login(req: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.email == req.email).first()
    if not customer or not customer.password_hash or not verify_password(req.password, customer.password_hash):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    token = create_token(customer.id, 'customer')
    return {'access_token': token, 'token_type': 'bearer', 'user_id': customer.id, 'name': customer.name, 'email': customer.email}

@router.post('/verify-otp')
def verify_otp_endpoint(req: OTPVerify, db: Session = Depends(get_db)):
    if req.role not in ['worker', 'customer']:
        raise HTTPException(status_code=400, detail="role must be 'worker' or 'customer'")

    if not verify_otp(req.phone, req.otp):
        raise HTTPException(status_code=400, detail='Invalid OTP')

    if req.role == 'worker':
        user = db.query(Worker).filter(Worker.phone == req.phone).first()
        if not user:
            user = Worker(
                id=str(uuid4()),
                phone=req.phone,
                name='',
                trust_score=0,
                trust_badge='Red',
                account_status='active'
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        user = db.query(Customer).filter(Customer.phone == req.phone).first()
        if not user:
            user = Customer(
                id=str(uuid4()),
                phone=req.phone,
                name=''
            )
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
