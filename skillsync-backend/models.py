from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from uuid import uuid4

class Worker(Base):
    __tablename__ = 'workers'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=True)
    phone = Column(String(20), unique=True, nullable=False)
    aadhaar_last4 = Column(String(4), nullable=True)
    aadhaar_verified = Column(Boolean, default=False)
    language = Column(String(5), default='hi')
    skill_type = Column(String(50), nullable=True)
    sub_skills = Column(String(200), nullable=True)
    experience_years = Column(Integer, nullable=True)
    bio_text = Column(Text, nullable=True)
    daily_rate = Column(Float, nullable=True)
    work_radius_km = Column(Integer, default=10)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    location_area = Column(String(100), nullable=True)
    voice_bio_path = Column(String(200), nullable=True)
    trust_score = Column(Integer, default=0)
    trust_badge = Column(String(10), default='Red')
    profile_complete = Column(Boolean, default=False)
    account_status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    password_hash = Column(String(200), nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    location_area = Column(String(100), nullable=True)
    emergency_contact1 = Column(String(20), nullable=True)
    emergency_contact2 = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkerPhoto(Base):
    __tablename__ = 'worker_photos'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    worker_id = Column(String(36), ForeignKey('workers.id'), nullable=False)
    file_path = Column(String(200), nullable=False)
    ai_tags = Column(String(300), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class JobRequest(Base):
    __tablename__ = 'job_requests'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False)
    worker_id = Column(String(36), ForeignKey('workers.id'), nullable=False)
    complaint_photo_path = Column(String(200), nullable=True)
    complaint_description = Column(Text, nullable=True)
    ai_issue_type = Column(String(50), nullable=True)
    ai_description = Column(Text, nullable=True)
    job_status = Column(String(20), default='pending')
    worker_response = Column(String(20), nullable=True)
    dispute_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class WorkLedger(Base):
    __tablename__ = 'work_ledger'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    worker_id = Column(String(36), ForeignKey('workers.id'), nullable=False)
    customer_id = Column(String(36), nullable=False)
    job_request_id = Column(String(36), ForeignKey('job_requests.id'), nullable=False)
    job_type = Column(String(50), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    completed_date = Column(Date, nullable=False)
    location_area = Column(String(100), nullable=True)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class QRCode(Base):
    __tablename__ = 'qr_codes'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    worker_id = Column(String(36), ForeignKey('workers.id'), nullable=False)
    job_request_id = Column(String(36), ForeignKey('job_requests.id'), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

class Call(Base):
    __tablename__ = 'calls'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    job_request_id = Column(String(36), ForeignKey('job_requests.id'), nullable=False)
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False)
    worker_id = Column(String(36), ForeignKey('workers.id'), nullable=False)
    call_start = Column(DateTime, nullable=True)
    call_end = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    worker_responded = Column(Boolean, nullable=True)
    post_call_rating = Column(Integer, nullable=True)
    post_call_review = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmergencyIncident(Base):
    __tablename__ = 'emergency_incidents'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = Column(String(36), ForeignKey('customers.id'), nullable=False)
    worker_id = Column(String(36), ForeignKey('workers.id'), nullable=False)
    job_request_id = Column(String(36), ForeignKey('job_requests.id'), nullable=True)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    police_station_name = Column(String(100), nullable=True)
    police_station_phone = Column(String(20), nullable=True)
    worker_flagged = Column(Boolean, default=True)
    status = Column(String(20), default='open')
    created_at = Column(DateTime, default=datetime.utcnow)

class IVRSession(Base):
    __tablename__ = 'ivr_sessions'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    phone = Column(String(20), nullable=False)
    current_state = Column(String(30), default='LANGUAGE_SELECT')
    language = Column(String(5), nullable=True)
    collected_data = Column(Text, default='{}')
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)