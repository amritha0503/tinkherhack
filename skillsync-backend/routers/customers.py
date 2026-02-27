from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import Customer
from auth import verify_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
security = HTTPBearer()

class CustomerRegister(BaseModel):
    name: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_area: Optional[str] = None
    emergency_contact1: Optional[str] = None
    emergency_contact2: Optional[str] = None

@router.post('/register')
def register_customer(
    data: CustomerRegister,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    customer = db.query(Customer).filter(Customer.id == payload['sub']).first()
    if not customer:
        raise HTTPException(status_code=404, detail='Customer not found. Please verify OTP first.')
    for key, value in data.dict(exclude_none=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return {'customer_id': customer.id, 'message': 'Profile saved successfully'}
