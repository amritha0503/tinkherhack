from sqlalchemy.orm import Session
from models import Worker, WorkLedger, Call, EmergencyIncident

def calculate_trust_score(worker_id: str, db: Session) -> dict:
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        return {
            'total_score': 0,
            'badge': 'Red',
            'breakdown': {
                'aadhaar': 0,
                'reviews': 0,
                'signoffs': 0,
                'response_rate': 0,
                'completeness': 0,
                'emergency_deduction': 0
            }
        }

    # Aadhaar score — max 20
    aadhaar_score = 20 if worker.aadhaar_verified else 0

    # Review score — max 25
    ledger_entries = db.query(WorkLedger).filter(WorkLedger.worker_id == worker_id).all()
    if ledger_entries:
        avg_rating = sum(e.rating for e in ledger_entries) / len(ledger_entries)
        review_score = round(avg_rating / 5 * 25)
    else:
        review_score = 0

    # Signoff score — max 25
    signoff_score = min(len(ledger_entries), 25)

    # Response rate score — max 15
    calls = db.query(Call).filter(Call.worker_id == worker_id).all()
    if calls:
        responded = sum(1 for c in calls if c.worker_responded is True)
        response_score = round((responded / len(calls)) * 15)
    else:
        response_score = 15  # give benefit of doubt if no calls yet

    # Completeness score — max 10
    fields = [
        worker.name,
        worker.skill_type,
        worker.bio_text,
        worker.experience_years,
        worker.location_lat,
        worker.daily_rate
    ]
    completeness_score = min(sum(2 for f in fields if f is not None), 10)

    # Emergency deduction
    emergencies = db.query(EmergencyIncident).filter(
        EmergencyIncident.worker_id == worker_id,
        EmergencyIncident.status == 'open'
    ).count()
    emergency_deduction = emergencies * 5

    # Total
    total = (aadhaar_score + review_score + signoff_score +
             response_score + completeness_score - emergency_deduction)
    total = max(0, min(100, total))

    badge = 'Green' if total >= 80 else 'Yellow' if total >= 50 else 'Red'

    # Persist to DB
    worker.trust_score = total
    worker.trust_badge = badge
    db.commit()

    return {
        'total_score': total,
        'badge': badge,
        'breakdown': {
            'aadhaar': aadhaar_score,
            'reviews': review_score,
            'signoffs': signoff_score,
            'response_rate': response_score,
            'completeness': completeness_score,
            'emergency_deduction': emergency_deduction
        }
    }