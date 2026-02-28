from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from database import engine, Base, init_db, SessionLocal
from sqlalchemy.orm import Session
from uuid import uuid4
import os
import uvicorn
import models
from src.routers import workers, customers, jobs, reviews, calls, emergency, ivr, auth_router
from src.routers.ai_call import router as ai_call_router

app = FastAPI(
    title='SkillSync API',
    description='Digital Identity for the Invisible Workforce',
    version='1.0.0',
    docs_url=None,  # disable default docs
    redoc_url=None  # disable default redoc
)

# Create all DB tables
models.Base.metadata.create_all(bind=engine)

# Create upload directories
os.makedirs('uploads/photos', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)

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

# Custom Swagger UI using CDN
@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        title='SkillSync API Docs',
        swagger_js_url='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js',
        swagger_css_url='https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css',
    )

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
                trust_score=87, trust_badge='Green', account_status='active',
                profile_complete=True,
                bio_text='Ramu is a certified electrician with 12 years of experience in residential and commercial wiring. He specializes in panel installations, safety audits, and fault repairs across Kozhikode.'
            ),
            models.Worker(
                id=str(uuid4()), name='Suresh Kumar', phone='9000000002',
                skill_type='Plumber', experience_years=8, daily_rate=600,
                location_lat=11.2650, location_lng=75.7850,
                location_area='Calicut Beach', aadhaar_verified=True,
                trust_score=72, trust_badge='Yellow', account_status='active',
                profile_complete=True,
                bio_text='Suresh is an experienced plumber skilled in pipe fitting, bathroom installation, and leak repairs. He has worked on over 200 homes in Calicut and surrounding areas.'
            ),
            models.Worker(
                id=str(uuid4()), name='Anand S', phone='9000000003',
                skill_type='Carpenter', experience_years=15, daily_rate=900,
                location_lat=11.2450, location_lng=75.7700,
                location_area='Palayam', aadhaar_verified=False,
                trust_score=45, trust_badge='Red', account_status='active',
                profile_complete=True,
                bio_text='Anand is a skilled carpenter specializing in custom furniture, door frames, and wooden flooring. 15 years of experience working with teak and plywood across Kerala.'
            ),
            models.Worker(
                id=str(uuid4()), name='Murugan R', phone='9000000004',
                skill_type='Painter', experience_years=6, daily_rate=500,
                location_lat=11.2700, location_lng=75.7950,
                location_area='Mavoor Road', aadhaar_verified=True,
                trust_score=61, trust_badge='Yellow', account_status='active',
                profile_complete=True,
                bio_text='Murugan is a professional painter experienced in interior and exterior painting, waterproofing, and texture finishes. Works cleanly and completes projects on time.'
            ),
            models.Worker(
                id=str(uuid4()), name='Biju Thomas', phone='9000000005',
                skill_type='Mason', experience_years=20, daily_rate=1000,
                location_lat=11.2550, location_lng=75.7750,
                location_area='SM Street', aadhaar_verified=True,
                trust_score=91, trust_badge='Green', account_status='active',
                profile_complete=True,
                bio_text='Biju is a master mason with 20 years of experience in brickwork, plastering, and concrete construction. He has led teams on major building projects across Kozhikode district.'
            ),
            models.Worker(
                id=str(uuid4()), name='Rajesh Verma', phone='9000000006',
                skill_type='Welder', experience_years=10, daily_rate=750,
                location_lat=11.2600, location_lng=75.7820,
                location_area='Nadakkav', aadhaar_verified=True,
                trust_score=80, trust_badge='Green', account_status='active',
                profile_complete=True,
                bio_text='Rajesh is a certified welder skilled in arc welding, gate fabrication, and metal repairs. He operates his own small workshop and serves both residential and industrial clients.'
            ),
            models.Worker(
                id=str(uuid4()), name='Lakshmi Devi', phone='9000000007',
                skill_type='Other', experience_years=5, daily_rate=400,
                location_lat=11.2520, location_lng=75.7780,
                location_area='West Hill', aadhaar_verified=True,
                trust_score=76, trust_badge='Green', account_status='active',
                profile_complete=True,
                bio_text='Lakshmi is a skilled domestic helper and cook specializing in Kerala and South Indian cuisine. She manages household work efficiently and is trusted by many families in West Hill.'
            ),
        ]
        
        for w in demo_workers:
            db.add(w)
        db.commit()
        print('[OK] Demo data seeded - workers added')
    except Exception as e:
        print(f'[ERROR] Seed failed: {e}')
        db.rollback()
    finally:
        db.close()

@app.on_event('startup')
async def startup_event():
    await init_db()
    seed_demo_data()

@app.get('/')
def root():
    return {
        'message': 'SkillSync API is running',
        'docs': '/docs',
        'version': '1.0.0'
    }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)