"""
AI Calling Agent Router
=======================
Simulates an AI phone call to a worker to build their portfolio.
Workers select their language, answer questions by voice/text,
and Gemini extracts a structured profile from their answers.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys, os, json, shutil, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import ai as ai_module
import models
from src.database import SessionLocal

router = APIRouter(prefix="/api/ai-call", tags=["AI Call"])

SUPPORTED_LANGUAGES = {
    "1": "Malayalam",
    "2": "Hindi",
    "3": "Tamil",
    "4": "Telugu",
    "5": "Bengali",
    "6": "Marathi",
    "7": "Kannada",
    "8": "English"
}

# Interview questions template (asked in selected language)
QUESTION_KEYS = [
    "name",
    "skill",
    "experience",
    "location",
    "daily_rate",
    "about"
]

QUESTIONS_ENGLISH = {
    "name":       "What is your full name?",
    "skill":      "What is your main skill or trade? For example: plumber, electrician, carpenter, cook, painter?",
    "experience": "How many years of experience do you have in this work?",
    "location":   "Which city or area do you work in?",
    "daily_rate": "How much do you charge per day for your work? Please say the amount in rupees.",
    "about":      "Tell us a little about yourself and the kind of work you have done before."
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class StartCallRequest(BaseModel):
    phone: str
    language_key: str   # "1" to "8"


class StartCallResponse(BaseModel):
    session_id: str
    language: str
    greeting: str
    questions: list[dict]   # [{key, question_text}]


class SubmitAnswersRequest(BaseModel):
    phone: str
    language: str
    answers: dict   # {question_key: answer_text}


@router.get("/languages")
def get_languages():
    """Return all supported languages with their dial keys."""
    return {
        "languages": [
            {"key": k, "name": v} for k, v in SUPPORTED_LANGUAGES.items()
        ]
    }


@router.post("/questions")
def get_questions(req: StartCallRequest):
    """
    Worker selects language (1-8).
    Returns translated interview questions in that language.
    """
    language = SUPPORTED_LANGUAGES.get(req.language_key)
    if not language:
        raise HTTPException(400, detail="Invalid language key. Choose 1-8.")

    questions = []

    if language == "English" or not ai_module.model:
        # Return English questions directly
        for key in QUESTION_KEYS:
            questions.append({"key": key, "question": QUESTIONS_ENGLISH[key]})
        greeting = (
            f"Hello! I am SkillSync AI assistant. "
            f"I will ask you {len(QUESTION_KEYS)} short questions to build your work profile. "
            f"Please answer in {language}."
        )
    else:
        try:
            prompt = f"""You are an AI calling agent for SkillSync, a platform that helps Indian informal workers (plumbers, electricians, carpenters etc.) get jobs.

Translate these interview questions into {language}. Keep translations simple and easy to understand for a worker with basic education.

Return ONLY a JSON object with these exact keys and their {language} translations:
{json.dumps(QUESTIONS_ENGLISH, ensure_ascii=False)}

Also add a key "greeting" with a warm greeting in {language} saying: "Hello! I am SkillSync AI assistant. I will ask you {len(QUESTION_KEYS)} short questions to build your work profile. Please answer in {language}."

Return ONLY valid JSON, nothing else."""
            response = ai_module.model.generate_content(prompt)
            clean = response.text.strip().replace('```json', '').replace('```', '').strip()
            translated = json.loads(clean)
            greeting = translated.pop("greeting", f"नमस्ते! मैं SkillSync AI हूँ।")
            for key in QUESTION_KEYS:
                questions.append({
                    "key": key,
                    "question": translated.get(key, QUESTIONS_ENGLISH[key])
                })
        except Exception:
            # Fallback to English
            for key in QUESTION_KEYS:
                questions.append({"key": key, "question": QUESTIONS_ENGLISH[key]})
            greeting = f"Hello! I am SkillSync AI. I will ask you {len(QUESTION_KEYS)} questions in {language}."

    return {
        "language": language,
        "greeting": greeting,
        "questions": questions
    }


@router.post("/extract-profile")
def extract_profile_from_answers(req: SubmitAnswersRequest):
    """
    After worker answers all questions (typed text or voice transcript),
    Gemini extracts a structured worker profile.
    """
    # Build a combined transcript from Q&A
    qa_pairs = []
    for key, answer in req.answers.items():
        q = QUESTIONS_ENGLISH.get(key, key)
        qa_pairs.append(f"Q: {q}\nA: {answer}")
    transcript = "\n\n".join(qa_pairs)

    profile = ai_module.extract_profile(transcript, req.language)
    # Also try to get name from the 'name' answer directly
    if req.answers.get("name"):
        profile["name"] = req.answers["name"]
    if req.answers.get("location"):
        profile["location_hint"] = req.answers["location"]

    return {
        "success": True,
        "language": req.language,
        "transcript": transcript,
        "profile": profile
    }


@router.post("/voice-answer")
async def transcribe_voice_answer(
    phone: str = Form(...),
    language: str = Form(...),
    question_key: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    Worker records audio for one question.
    Returns transcribed text so frontend can show it and user can confirm.
    """
    if not ai_module.model:
        raise HTTPException(503, detail="AI service unavailable. Use text input instead.")

    # browser MediaRecorder produces webm; filename may be empty/None
    filename = audio.filename or ""
    suffix = os.path.splitext(filename)[1] if filename else ".webm"
    if not suffix:
        suffix = ".webm"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        shutil.copyfileobj(audio.file, tmp)
        tmp.close()
        transcript = ai_module.voice_to_text(tmp.name, language)
    except Exception as e:
        raise HTTPException(500, detail=f"Transcription failed: {str(e)}")
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

    return {"question_key": question_key, "transcript": transcript}


@router.post("/save-profile")
def save_worker_profile(phone: str, profile: dict, db: Session = Depends(get_db)):
    """
    Save or update worker profile in the database after AI call completes.
    """
    worker = db.query(models.Worker).filter(models.Worker.phone == phone).first()
    if not worker:
        worker = models.Worker(phone=phone)
        db.add(worker)

    worker.name = profile.get("name") or worker.name
    worker.skill_type = profile.get("skill_type") or worker.skill_type
    worker.experience_years = profile.get("experience_years") or worker.experience_years
    worker.daily_rate = profile.get("daily_rate") or worker.daily_rate
    worker.bio_text = profile.get("bio_text") or profile.get("bio_english") or worker.bio_text
    worker.profile_complete = True

    db.commit()
    db.refresh(worker)

    return {
        "success": True,
        "worker_id": worker.id,
        "message": f"Profile saved for {worker.name or phone}"
    }
