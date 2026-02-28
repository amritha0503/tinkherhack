"""
Seed 10 sample workers around Kozhikode, Kerala.
Run from the skillsync-backend directory:
    python seed_workers.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, Base, engine
from models import Worker
from uuid import uuid4

Base.metadata.create_all(bind=engine)

WORKERS = [
    {
        "name": "Mohammed Ashraf",
        "phone": "9800000001",
        "skill_type": "Electrician",
        "experience_years": 7,
        "daily_rate": 700,
        "location_area": "Cherootty Road",
        "location_lat": 11.2530,
        "location_lng": 75.7792,
        "trust_score": 82,
        "trust_badge": "Green",
        "aadhaar_verified": True,
        "bio_text": "Licensed electrician specialising in residential wiring and solar panel installations.",
        "work_radius_km": 20,
    },
    {
        "name": "Priya Nair",
        "phone": "9800000002",
        "skill_type": "Cook",
        "experience_years": 5,
        "daily_rate": 500,
        "location_area": "Beach Road",
        "location_lat": 11.2476,
        "location_lng": 75.7739,
        "trust_score": 74,
        "trust_badge": "Yellow",
        "aadhaar_verified": True,
        "bio_text": "Experienced in Kerala cuisine, catering and home cooking services.",
        "work_radius_km": 15,
    },
    {
        "name": "Thomas Antony",
        "phone": "9800000003",
        "skill_type": "Mason",
        "experience_years": 15,
        "daily_rate": 900,
        "location_area": "Panniyankara",
        "location_lat": 11.1900,
        "location_lng": 75.7900,
        "trust_score": 88,
        "trust_badge": "Green",
        "aadhaar_verified": True,
        "bio_text": "Master mason with 15 years experience in brickwork, plastering and tile fixing.",
        "work_radius_km": 30,
    },
    {
        "name": "Vijayan K",
        "phone": "9800000004",
        "skill_type": "Carpenter",
        "experience_years": 10,
        "daily_rate": 750,
        "location_area": "Feroke",
        "location_lat": 11.2050,
        "location_lng": 75.8100,
        "trust_score": 79,
        "trust_badge": "Green",
        "aadhaar_verified": True,
        "bio_text": "Custom furniture making, door and window fitting, interior woodwork.",
        "work_radius_km": 25,
    },
    {
        "name": "Sunitha K",
        "phone": "9800000005",
        "skill_type": "Painter",
        "experience_years": 6,
        "daily_rate": 550,
        "location_area": "Ramanattukara",
        "location_lat": 11.1822,
        "location_lng": 75.8200,
        "trust_score": 65,
        "trust_badge": "Yellow",
        "aadhaar_verified": False,
        "bio_text": "Interior and exterior painting, texture coating and waterproofing.",
        "work_radius_km": 20,
    },
    {
        "name": "Abdul Rehman",
        "phone": "9800000006",
        "skill_type": "Plumber",
        "experience_years": 9,
        "daily_rate": 650,
        "location_area": "Pallikkal",
        "location_lat": 11.3050,
        "location_lng": 75.7900,
        "trust_score": 83,
        "trust_badge": "Green",
        "aadhaar_verified": True,
        "bio_text": "Expert in pipe fitting, bathroom fitting and overhead tank installations.",
        "work_radius_km": 25,
    },
    {
        "name": "Deepa Menon",
        "phone": "9800000007",
        "skill_type": "Welder",
        "experience_years": 8,
        "daily_rate": 800,
        "location_area": "Beypore",
        "location_lat": 11.1700,
        "location_lng": 75.8089,
        "trust_score": 76,
        "trust_badge": "Green",
        "aadhaar_verified": True,
        "bio_text": "MIG and arc welding for gates, grills and structural steel work.",
        "work_radius_km": 30,
    },
    {
        "name": "Santhosh V",
        "phone": "9800000008",
        "skill_type": "Electrician",
        "experience_years": 4,
        "daily_rate": 600,
        "location_area": "Koyilandy",
        "location_lat": 11.4400,
        "location_lng": 75.7000,
        "trust_score": 58,
        "trust_badge": "Yellow",
        "aadhaar_verified": False,
        "bio_text": "Electrical repair, motor winding and industrial electrical maintenance.",
        "work_radius_km": 20,
    },
    {
        "name": "Meera R",
        "phone": "9800000009",
        "skill_type": "Mason",
        "experience_years": 12,
        "daily_rate": 850,
        "location_area": "Vatakara",
        "location_lat": 11.6000,
        "location_lng": 75.5917,
        "trust_score": 90,
        "trust_badge": "Green",
        "aadhaar_verified": True,
        "bio_text": "Specialised in stone masonry, flooring and commercial construction projects.",
        "work_radius_km": 40,
    },
    {
        "name": "Harikrishnan P",
        "phone": "9800000010",
        "skill_type": "Carpenter",
        "experience_years": 3,
        "daily_rate": 500,
        "location_area": "Mukkom",
        "location_lat": 11.3917,
        "location_lng": 75.9167,
        "trust_score": 42,
        "trust_badge": "Red",
        "aadhaar_verified": False,
        "bio_text": "General carpentry, furniture repair and wooden roofing work.",
        "work_radius_km": 15,
    },
]

db = SessionLocal()
added = 0
skipped = 0
for w in WORKERS:
    existing = db.query(Worker).filter(Worker.phone == w["phone"]).first()
    if existing:
        # update coordinates & details
        for k, v in w.items():
            setattr(existing, k, v)
        skipped += 1
    else:
        worker = Worker(id=str(uuid4()), profile_complete=True, account_status="active", **w)
        db.add(worker)
        added += 1

db.commit()
db.close()
print(f"Done. Added: {added}, Updated: {skipped}")
