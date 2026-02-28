"""
AI Calling Agent Router
=======================
Simulates an AI phone call to a worker to build their portfolio.
Workers select their language, answer questions by voice/text,
and Gemini extracts a structured profile from their answers.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys, os, json, shutil, tempfile, io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import ai as ai_module
import models
from src.database import SessionLocal

router = APIRouter(prefix="/api/ai-call", tags=["AI Call"])

# gTTS language codes for Indian languages
GTTS_LANG = {
    "Malayalam": "ml",
    "Hindi":     "hi",
    "Tamil":     "ta",
    "Telugu":    "te",
    "Bengali":   "bn",
    "Marathi":   "mr",
    "Kannada":   "kn",
    "English":   "en",
}

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
    "about",
    "aadhaar_last4",
    "aadhaar_otp"
]

QUESTIONS_ENGLISH = {
    "name":          "What is your full name?",
    "skill":         "What is your main skill or trade? For example: plumber, electrician, carpenter, cook, painter?",
    "experience":    "How many years of experience do you have in this work?",
    "location":      "Which city or area do you work in?",
    "daily_rate":    "How much do you charge per day for your work? Please say the amount in rupees.",
    "about":         "Tell us a little about yourself and the kind of work you have done before.",
    "aadhaar_last4": "Please tell us the last 4 digits of your Aadhaar card for identity verification.",
    "aadhaar_otp":   "We have sent a one-time password to the mobile number registered with your Aadhaar. Please say the OTP now."
}

# In-memory OTP store: {phone: {otp, aadhaar_last4, verified}}
_otp_store: dict = {}

# Hardcoded translations — no Gemini dependency for core questions
QUESTIONS_TRANSLATED = {
    "Malayalam": {
        "greeting":        "നമസ്‌കാരം! ഞാൻ SkillSync AI ആണ്. നിങ്ങളുടെ ജോലി പ്രൊഫൈൽ ഉണ്ടാക്കാൻ ഞാൻ എട്ട് ചോദ്യങ്ങൾ ചോദിക്കും. ദയവായി മലയാളത്തിൽ ഉത്തരം പറയുക.",
        "name":            "നിങ്ങളുടെ പൂർണ്ണ പേര് എന്താണ്?",
        "skill":           "നിങ്ങളുടെ പ്രധാന തൊഴിൽ അല്ലെങ്കിൽ കഴിവ് എന്താണ്? ഉദാഹരണം: പ്ലംബർ, ഇലക്ട്രീഷ്യൻ, ആശാരി, പാചകക്കാരൻ, പെയിന്റർ?",
        "experience":      "ഈ ജോലിയിൽ നിങ്ങൾക്ക് എത്ര വർഷത്തെ അനുഭവം ഉണ്ട്?",
        "location":        "നിങ്ങൾ ഏത് നഗരത്തിൽ അല്ലെങ്കിൽ പ്രദേശത്ത് ജോലി ചെയ്യുന്നു?",
        "daily_rate":      "ഒരു ദിവസം ജോലിക്ക് നിങ്ങൾ എത്ര രൂപ ഈടാക്കുന്നു?",
        "about":           "നിങ്ങളെക്കുറിച്ചും നിങ്ങൾ മുൻപ് ചെയ്ത ജോലിയെക്കുറിച്ചും അൽപ്പം പറയൂ.",
        "aadhaar_last4":   "ദയവായി നിങ്ങളുടെ ആധാർ കാർഡിന്റെ അവസാന 4 അക്കങ്ങൾ പറയൂ. ഇത് നിങ്ങളുടെ ഐഡന്റിറ്റി സ്ഥിരീകരിക്കാൻ ആണ്.",
        "aadhaar_otp":     "നിങ്ങളുടെ ആധാറുമായി ബന്ധിപ്പിച്ച മൊബൈൽ നമ്പറിലേക്ക് ഒരു OTP അയച്ചിട്ടുണ്ട്. ദയവായി ആ OTP ഇപ്പോൾ പറയൂ.",
    },
    "Hindi": {
        "greeting":        "नमस्ते! मैं SkillSync AI हूँ। आपकी वर्क प्रोफ़ाइल बनाने के लिए मैं आपसे आठ सवाल पूछूँगा। कृपया हिंदी में जवाब दें।",
        "name":            "आपका पूरा नाम क्या है?",
        "skill":           "आपका मुख्य काम या हुनर क्या है? जैसे: प्लंबर, इलेक्ट्रीशियन, कारपेंटर, कुक, पेंटर?",
        "experience":      "आपको इस काम में कितने साल का अनुभव है?",
        "location":        "आप किस शहर या इलाके में काम करते हैं?",
        "daily_rate":      "आप एक दिन के काम के लिए कितने रुपये लेते हैं?",
        "about":           "अपने बारे में और अपने पहले के काम के बारे में थोड़ा बताइए।",
        "aadhaar_last4":   "कृपया पहचान सत्यापन के लिए अपने आधार कार्ड के अंतिम 4 अंक बताएं।",
        "aadhaar_otp":     "आपके आधार से जुड़े मोबाइल नंबर पर एक OTP भेजा गया है। कृपया वह OTP अभी बोलें।",
    },
    "Tamil": {
        "greeting":        "வணக்கம்! நான் SkillSync AI. உங்கள் வேலை சுயவிவரம் உருவாக்க எட்டு கேள்விகள் கேட்கிறேன். தமிழில் பதில் சொல்லுங்கள்.",
        "name":            "உங்கள் முழு பெயர் என்ன?",
        "skill":           "உங்கள் முக்கிய திறன் அல்லது தொழில் என்ன? எடுத்துக்காட்டாக: பிளம்பர், மின்சாரி, தச்சர், சமையல்காரர், சாயம் பூசுபவர்?",
        "experience":      "இந்த வேலையில் உங்களுக்கு எத்தனை வருட அனுபவம் உள்ளது?",
        "location":        "நீங்கள் எந்த நகரம் அல்லது பகுதியில் வேலை செய்கிறீர்கள்?",
        "daily_rate":      "நீங்கள் ஒரு நாளுக்கு எவ்வளவு ரூபாய் கட்டணம் வசூலிக்கிறீர்கள்?",
        "about":           "உங்களைப் பற்றியும் நீங்கள் முன்பு செய்த வேலைகளைப் பற்றியும் கொஞ்சம் சொல்லுங்கள்.",
        "aadhaar_last4":   "அடையாளச் சரிபார்ப்புக்காக உங்கள் ஆதார் கார்டின் கடைசி 4 இலக்கங்களை சொல்லுங்கள்.",
        "aadhaar_otp":     "உங்கள் ஆதாருடன் இணைக்கப்பட்ட மொபைல் எண்ணுக்கு ஒரு OTP அனுப்பப்பட்டுள்ளது. தயவுசெய்து அந்த OTP-ஐ இப்போது சொல்லுங்கள்.",
    },
    "Telugu": {
        "greeting":        "నమస్కారం! నేను SkillSync AI. మీ పని ప్రొఫైల్ తయారు చేయడానికి ఎనిమిది ప్రశ్నలు అడుగుతాను. దయచేసి తెలుగులో సమాధానం చెప్పండి.",
        "name":            "మీ పూర్తి పేరు ఏమిటి?",
        "skill":           "మీ ప్రధాన నైపుణ్యం లేదా వృత్తి ఏమిటి? ఉదాహరణకు: ప్లంబర్, ఎలక్ట్రీషియన్, కార్పెంటర్, వంట మనిషి, పెయింటర్?",
        "experience":      "ఈ పనిలో మీకు ఎన్ని సంవత్సరాల అనుభవం ఉంది?",
        "location":        "మీరు ఏ నగరంలో లేదా ప్రాంతంలో పని చేస్తారు?",
        "daily_rate":      "మీరు ఒక రోజు పనికి ఎంత రూపాయలు తీసుకుంటారు?",
        "about":           "మీ గురించి మరియు మీరు ముందు చేసిన పనుల గురించి కొంచెం చెప్పండి.",
        "aadhaar_last4":   "దయచేసి గుర్తింపు ధృవీకరణ కోసం మీ ఆధార్ కార్డ్ చివరి 4 అంకెలు చెప్పండి.",
        "aadhaar_otp":     "మీ ఆధార్‌తో లింక్ చేయబడిన మొబైల్ నంబర్‌కు OTP పంపబడింది. దయచేసి ఆ OTP ఇప్పుడు చెప్పండి.",
    },
    "Bengali": {
        "greeting":        "নমস্কার! আমি SkillSync AI। আপনার কাজের প্রোফাইল তৈরি করতে আটটি প্রশ্ন জিজ্ঞেস করব। দয়া করে বাংলায় উত্তর দিন।",
        "name":            "আপনার পুরো নাম কী?",
        "skill":           "আপনার প্রধান দক্ষতা বা পেশা কী? যেমন: প্লাম্বার, ইলেকট্রিশিয়ান, কার্পেন্টার, রান্নার কাজ, পেইন্টার?",
        "experience":      "এই কাজে আপনার কত বছরের অভিজ্ঞতা আছে?",
        "location":        "আপনি কোন শহর বা এলাকায় কাজ করেন?",
        "daily_rate":      "আপনি প্রতিদিনের কাজের জন্য কত টাকা নেন?",
        "about":           "আপনার সম্পর্কে এবং আগে যে কাজ করেছেন সে সম্পর্কে একটু বলুন।",
        "aadhaar_last4":   "পরিচয় যাচাইয়ের জন্য দয়া করে আপনার আধার কার্ডের শেষ ৪ সংখ্যা বলুন।",
        "aadhaar_otp":     "আপনার আধারের সাথে সংযুক্ত মোবাইল নম্বরে একটি OTP পাঠানো হয়েছে। দয়া করে এখনই সেই OTP বলুন।",
    },
    "Marathi": {
        "greeting":        "नमस्कार! मी SkillSync AI आहे. तुमची कामाची प्रोफाईल बनवण्यासाठी मी आठ प्रश्न विचारेन. कृपया मराठीत उत्तर द्या.",
        "name":            "तुमचे पूर्ण नाव काय आहे?",
        "skill":           "तुमचे मुख्य कौशल्य किंवा व्यवसाय काय आहे? उदाहरणार्थ: प्लंबर, इलेक्ट्रिशियन, सुतार, स्वयंपाकी, रंगारी?",
        "experience":      "या कामात तुम्हाला किती वर्षांचा अनुभव आहे?",
        "location":        "तुम्ही कोणत्या शहरात किंवा भागात काम करता?",
        "daily_rate":      "तुम्ही एक दिवसाच्या कामासाठी किती रुपये घेता?",
        "about":           "स्वतःबद्दल आणि आधी केलेल्या कामाबद्दल थोडे सांगा.",
        "aadhaar_last4":   "ओळख पडताळणीसाठी कृपया तुमच्या आधार कार्डचे शेवटचे 4 अंक सांगा.",
        "aadhaar_otp":     "तुमच्या आधारशी जोडलेल्या मोबाइल नंबरवर एक OTP पाठवण्यात आला आहे. कृपया तो OTP आत्ता सांगा.",
    },
    "Kannada": {
        "greeting":        "ನಮಸ್ಕಾರ! ನಾನು SkillSync AI. ನಿಮ್ಮ ಕೆಲಸದ ಪ್ರೊಫೈಲ್ ಮಾಡಲು ಎಂಟು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ. ದಯವಿಟ್ಟು ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ.",
        "name":            "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?",
        "skill":           "ನಿಮ್ಮ ಮುಖ್ಯ ಕೌಶಲ್ಯ ಅಥವಾ ವೃತ್ತಿ ಏನು? ಉದಾಹರಣೆ: ಪ್ಲಂಬರ್, ಎಲೆಕ್ಟ್ರಿಷಿಯನ್, ಬಡಗಿ, ಅಡಿಗೆ ಮಾಡುವವರು, ಬಣ್ಣ ಹಚ್ಚುವವರು?",
        "experience":      "ಈ ಕೆಲಸದಲ್ಲಿ ನಿಮಗೆ ಎಷ್ಟು ವರ್ಷಗಳ ಅನುಭವ ಇದೆ?",
        "location":        "ನೀವು ಯಾವ ನಗರ ಅಥವಾ ಪ್ರದೇಶದಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತೀರಿ?",
        "daily_rate":      "ನೀವು ಒಂದು ದಿನದ ಕೆಲಸಕ್ಕೆ ಎಷ್ಟು ರೂಪಾಯಿ ತೆಗೆದುಕೊಳ್ಳುತ್ತೀರಿ?",
        "about":           "ನಿಮ್ಮ ಬಗ್ಗೆ ಮತ್ತು ನೀವು ಮೊದಲು ಮಾಡಿದ ಕೆಲಸಗಳ ಬಗ್ಗೆ ಸ್ವಲ್ಪ ಹೇಳಿ.",
        "aadhaar_last4":   "ಗುರುತಿನ ಪರಿಶೀಲನೆಗಾಗಿ ದಯವಿಟ್ಟು ನಿಮ್ಮ ಆಧಾರ್ ಕಾರ್ಡ್‌ನ ಕೊನೆಯ 4 ಅಂಕಿಗಳನ್ನು ಹೇಳಿ.",
        "aadhaar_otp":     "ನಿಮ್ಮ ಆಧಾರ್‌ಗೆ ಲಿಂಕ್ ಆಗಿರುವ ಮೊಬೈಲ್ ನಂಬರ್‌ಗೆ OTP ಕಳುಹಿಸಲಾಗಿದೆ. ದಯವಿಟ್ಟು ಆ OTP ಈಗ ಹೇಳಿ.",
    },
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


class TTSRequest(BaseModel):
    text: str
    language: str  # e.g. "Malayalam", "Hindi", "English"


class TranslateRequest(BaseModel):
    text: str
    source_language: str  # e.g. "Malayalam", "Hindi"


@router.post("/translate")
def translate_to_english(req: TranslateRequest):
    """
    Translate text from any Indian language to English.
    Uses deep-translator (free, no API key required).
    """
    if req.source_language == "English":
        return {"translated": req.text, "original": req.text}
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target='en').translate(req.text)
        return {"translated": translated, "original": req.text}
    except Exception as e:
        raise HTTPException(500, detail=f"Translation failed: {str(e)}")


class GenerateOTPRequest(BaseModel):
    phone: str
    aadhaar_last4: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


@router.post("/generate-otp")
def generate_otp(req: GenerateOTPRequest):
    """
    Simulate sending an OTP to the Aadhaar-registered mobile number.
    In production this would call an SMS gateway.
    For demo: generates a 6-digit OTP and returns it (so operator can relay it).
    """
    import random
    otp = str(random.randint(100000, 999999))
    _otp_store[req.phone] = {"otp": otp, "aadhaar_last4": req.aadhaar_last4, "verified": False}
    # In a real system we would NOT return the OTP — it would be sent via SMS.
    # For demo purposes we return it so the operator/tester can see it.
    return {
        "success": True,
        "message": f"OTP sent to Aadhaar-registered mobile for last-4 digits {req.aadhaar_last4}",
        "demo_otp": otp   # Remove this field in production!
    }


@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest):
    """
    Verify the OTP spoken/typed by the worker.
    Returns verified=True if the OTP matches.
    """
    record = _otp_store.get(req.phone)
    if not record:
        raise HTTPException(400, detail="No OTP found for this phone. Please generate OTP first.")
    if record["otp"] == req.otp.strip():
        _otp_store[req.phone]["verified"] = True
        return {"verified": True, "message": "Aadhaar identity verified successfully."}
    return {"verified": False, "message": "OTP does not match. Please try again."}


@router.post("/tts")
def text_to_speech(req: TTSRequest):
    """
    Convert text to speech using gTTS (Google TTS).
    Returns MP3 audio stream in the requested language.
    Works for all Indian languages without any API key.
    """
    from gtts import gTTS
    lang_code = GTTS_LANG.get(req.language, "en")
    try:
        tts = gTTS(text=req.text, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return StreamingResponse(buf, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(500, detail=f"TTS failed: {str(e)}")


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

    if language == "English":
        for key in QUESTION_KEYS:
            questions.append({"key": key, "question": QUESTIONS_ENGLISH[key]})
        greeting = (
            f"Hello! I am SkillSync AI assistant. "
            f"I will ask you {len(QUESTION_KEYS)} short questions to build your work profile. "
            f"Please answer in English."
        )
    elif language in QUESTIONS_TRANSLATED:
        # Use hardcoded translations — always works, no API dependency
        t = QUESTIONS_TRANSLATED[language]
        greeting = t["greeting"]
        for key in QUESTION_KEYS:
            questions.append({"key": key, "question": t[key]})
    else:
        # Fallback for any future language not yet hardcoded
        for key in QUESTION_KEYS:
            questions.append({"key": key, "question": QUESTIONS_ENGLISH[key]})
        greeting = f"Hello! I am SkillSync AI. I will ask you {len(QUESTION_KEYS)} questions. Please answer in {language}."

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
