from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import EmergencyIncident, Worker, Customer
from auth import verify_token
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

router = APIRouter()
security = HTTPBearer()

POLICE_STATION = {
    'name': 'Kozhikode Central Police Station',
    'phone': '0495-2701100'
}

class EmergencyTrigger(BaseModel):
    job_request_id: Optional[str] = None
    location_lat: float
    location_lng: float
    worker_id: str

@router.post('/trigger')
def trigger_emergency(
    data: EmergencyTrigger,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    customer = db.query(Customer).filter(Customer.id == payload['sub']).first()
    worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
    incident = EmergencyIncident(
        id=str(uuid4()),
        customer_id=payload['sub'],
        worker_id=data.worker_id,
        job_request_id=data.job_request_id,
        location_lat=data.location_lat,
        location_lng=data.location_lng,
        police_station_name=POLICE_STATION['name'],
        police_station_phone=POLICE_STATION['phone'],
        worker_flagged=True,
        status='open'
    )
    db.add(incident)
    if worker:
        worker.account_status = 'flagged'
    db.commit()
    customer_name = customer.name if customer else 'Unknown'
    worker_name = worker.name if worker else 'Unknown'
    print(f'🚨 ALERT: Customer {customer_name} needs help at {data.location_lat},{data.location_lng}. Worker: {worker_name}. Incident ID: {incident.id}')
    return {
        'incident_id': incident.id,
        'worker_flagged': True,
        'police_station': POLICE_STATION,
        'message': 'Emergency logged. Help is coming.'
    }

@router.get('/{incident_id}')
def get_incident(
    incident_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    incident = db.query(EmergencyIncident).filter(EmergencyIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail='Incident not found')
    return incident