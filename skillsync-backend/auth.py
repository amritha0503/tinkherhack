from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
import random

OTP_STORE = {}
JWT_SECRET = 'skillsync-hackathon-secret'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 60 * 24

def send_otp(phone: str) -> bool:
    otp = str(random.randint(100000, 999999))
    OTP_STORE[phone] = otp
    print(f'[OTP] Phone: {phone} => OTP: {otp}')  # Visible in server logs
    return True

def verify_otp(phone: str, otp: str) -> bool:
    return OTP_STORE.get(phone) == otp

def create_token(user_id: str, role: str) -> str:
    payload = {
        'sub': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token'
        )

import hashlib, os

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f'{salt}${h}'

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, h = hashed.split('$', 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    except Exception:
        return False