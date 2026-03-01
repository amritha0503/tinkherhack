from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
import models
from routers import workers, customers, jobs, reviews, calls, emergency, ivr, auth_router
from src.routers.ai_call import router as ai_call_router
from sqlalchemy.orm import Session
from database import SessionLocal
from uuid import uuid4
import os

# Create all DB tables
models.Base.metadata.create_all(bind=engine)

# Create upload directories
os.makedirs('uploads/photos', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)

app = FastAPI(
    title='SkillSync API',
    description='Digital Identity for the Invisible Workforce',
    version='1.0.0'
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Static files
app.mount('/uploads', StaticFiles(directory='uploads'), name='uploads')

# Routers
app.include_router(auth_router.router,  prefix='/api/auth',      tags=['Auth'])
app.include_router(workers.router,      prefix='/api/workers',   tags=['Workers'])
app.include_router(customers.router,    prefix='/api/customers', tags=['Customers'])
app.include_router(jobs.router,         prefix='/api/jobs',      tags=['Jobs'])
app.include_router(reviews.router,      prefix='/api/reviews',   tags=['Reviews'])
app.include_router(calls.router,        prefix='/api/calls',     tags=['Calls'])
app.include_router(emergency.router,    prefix='/api/emergency', tags=['Emergency'])
app.include_router(ivr.router,          prefix='/api/ivr',       tags=['IVR'])
app.include_router(ai_call_router)

def seed_demo_data():
    db: Session = SessionLocal()
    try:
        if db.query(models.Worker).count() > 0:
            print('[INFO] Demo data already exists, skipping seed.')
            return
        demo_workers = [
            models.Worker(
                id=str(uuid4()), name='Ramu Naidu', phone='9000000001',
                skill_type='Electrician', experience_years=12, daily_rate=800,
                location_lat=11.2588, location_lng=75.7804,
                location_area='Kozhikode', aadhaar_verified=True,
                trust_score=87, trust_badge='Green', account_status='active'
            ),
            models.Worker(
                id=str(uuid4()), name='Suresh Kumar', phone='9000000002',
                skill_type='Plumber', experience_years=8, daily_rate=600,
                location_lat=11.2650, location_lng=75.7850,
                location_area='Calicut Beach', aadhaar_verified=True,
                trust_score=72, trust_badge='Yellow', account_status='active'
            ),
            models.Worker(
                id=str(uuid4()), name='Anand S', phone='9000000003',
                skill_type='Carpenter', experience_years=15, daily_rate=900,
                location_lat=11.2450, location_lng=75.7700,
                location_area='Palayam', aadhaar_verified=False,
                trust_score=45, trust_badge='Red',    account_status='active'
            ),
            models.Worker(
                id=str(uuid4()), name='Murugan R', phone='9000000004',
                skill_type='Painter', experience_years=6, daily_rate=500,
                location_lat=11.2700, location_lng=75.7950,
                location_area='Mavoor Road', aadhaar_verified=True,
                trust_score=61, trust_badge='Yellow', account_status='active'
            ),
            models.Worker(
                id=str(uuid4()), name='Biju Thomas', phone='9000000005',
                skill_type='Mason', experience_years=20, daily_rate=1000,
                location_lat=11.2550, location_lng=75.7750,
                location_area='SM Street', aadhaar_verified=True,
                trust_score=91, trust_badge='Green',  account_status='active'
            ),
        ]
        for w in demo_workers:
            db.add(w)
        db.commit()
        print('[OK] Demo data seeded - 5 workers added')
    except Exception as e:
        print(f'[ERROR] Seed failed: {e}')
        db.rollback()
    finally:
        db.close()

@app.on_event('startup')
def startup_event():
    seed_demo_data()

@app.get('/')
def root():
    return {
        'message': 'SkillSync API is running',
        'docs': '/docs',
        'version': '1.0.0'
    }