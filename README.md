<p align="center">
  <img src="./img.png" alt="SkillSync Banner" width="100%">
</p>

# SkillSync 🛠️ — Digital Identity for the Invisible Workforce

## Basic Details

### Team Name: Antigravity

### Team Members
- Member 1: Amritha — Mar Athanasius College Of Engineering
- Member 2: Neha — Mar Athanasius College Of Engineering

### Hosted Project Link
- **Frontend:** https://tinkherhack-69tm-dkjvagqi2-neha-georges-projects.vercel.app/
- **Backend API:** https://tinkherhack-euby.onrender.com
- **API Docs:** https://tinkherhack-euby.onrender.com/docs

---

### Project Description
SkillSync is a voice-first, multilingual platform that gives informal sector workers (plumbers, electricians, carpenters, masons) a verified digital identity — with zero literacy barrier. Workers onboard via an AI phone call in their native language, get Aadhaar-verified, and receive a live portfolio with a Trust Score. Customers find and call workers sorted by distance, then leave tamper-proof verified reviews.

### The Problem Statement
India has 450+ million informal skilled workers — plumbers, electricians, carpenters, painters — who are digitally invisible. They lose high-paying formal gigs because they have no verifiable digital presence, no review history, and no way to prove their skills. Customers can't trust them. Workers can't grow.

### The Solution
SkillSync onboards workers through a guided AI voice call in 8 Indian languages — no typing, no smartphone required. It verifies identity via Aadhaar OTP, converts voice answers into a structured profile, calculates a Trust Score from verified job history, and lets customers find, call, and review workers — all through one platform.

---

## Technical Details

### Technologies / Components Used

**For Software:**
- **Languages:** Python, JavaScript (JSX)
- **Frontend Framework:** React 18 + Vite + Tailwind CSS
- **Backend Framework:** FastAPI (Python)
- **Database:** SQLite (dev) / PostgreSQL (prod via SQLAlchemy)
- **AI / NLP:** Google Gemini 2.0 Flash — profile extraction, complaint photo analysis
- **Text-to-Speech:** gTTS (Google Text-to-Speech) — free, no API key, 8 Indian languages
- **Translation:** deep-translator (GoogleTranslator) — auto language detection → English
- **Speech Recognition:** Web Speech API (browser-native, multilingual)
- **Authentication:** OTP-based (phone + Aadhaar last-4 + in-memory OTP store)
- **Calling:** In-app WebRTC/masked call simulation with live timer + post-call review
- **Libraries:** axios, react-router-dom, react-hot-toast, lucide-react, python-jose, python-multipart, uvicorn
- **Tools:** VS Code, Git, Render (backend hosting), Vercel (frontend hosting)

---

## Features

### 🎙️ Voice-First AI Onboarding (Zero Literacy Barrier)
Worker receives an AI call. The system asks 8 guided questions in their chosen Indian language (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, English). All answers are spoken — no typing needed. Supports code-switching (Hinglish, Manglish, Tanglish).

### 🆔 Aadhaar Identity Verification via OTP
During the AI call, the worker provides the last 4 digits of their Aadhaar card. An OTP is sent to the Aadhaar-registered mobile. Verification unlocks the **Identity Verified ✓** badge on their profile. No full Aadhaar stored — only the last 4 digits.

### 🤖 AI Profile Extraction (Google Gemini)
Voice answers are transcribed and sent to Gemini, which extracts a structured profile: `skill_type`, `experience_years`, `work_areas`, `daily_rate`, `specializations`, and writes a professional English bio — even from fragmented spoken answers.

### ⭐ Dynamic Trust Score (0–100)
Workers get a real-time Trust Score based on:
- Aadhaar Verification → 20 pts
- Customer Reviews (avg rating) → 25 pts
- QR-verified Job Completions → 25 pts
- Call Response Rate → 15 pts
- Profile Completeness → 10 pts
- Zero Complaints → 5 pts

Displayed as a colored badge: 🟢 Green (80+), 🟡 Yellow (50–79), 🔴 Red (below 50).

### 📍 Distance-Sorted Worker Search
Customer's GPS or manual location is used to sort all workers by ascending distance. Advanced filters: skill type, distance radius, min Trust Score, daily rate range, language spoken, availability.

### 📞 In-App Calling Interface
Customer calls worker without sharing private numbers. Full call UI: ringing animation → connected screen with live timer, sound wave, mute/speaker controls → call ended. Post-call review auto-appears after the call ends.

### 🔒 Verified Work Ledger (QR Seal)
After job completion, worker generates a unique QR code. Customer scans it to unlock the review form. This links every review to a physical, real transaction — reviews cannot be faked. Each entry is append-only (no edits or deletions allowed).

### 🌐 Multilingual TTS + Real-Time Translation
AI questions are read aloud in the worker's chosen language using gTTS. Worker speaks in their language — answers are auto-translated to English using Google Translate (`source=auto`). If translation fails, the UI gracefully falls back to a typing mode with a clear prompt.

### 🚨 Emergency Safety Button
Persistent emergency button visible during active jobs. Triggered by a 3-second hold. Actions: captures GPS, calls nearest police station, sends SMS to 2 emergency contacts with worker's verified ID and location, flags worker account for immediate review.

### 👤 Customer Dashboard & Worker Card
Full worker profile page: photo gallery, skill badge, experience, Trust Score, distance, rate, languages, bio, reviews, and call button. Workers appear as cards with distance badges, trust badge colors, and quick-view stats.

---

## Implementation

### For Software:

#### Installation

```bash
# Clone the repo
git clone https://github.com/amritha0503/tinkherhack.git
cd tinkherhack

# Backend
cd skillsync-backend
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_GEMINI_API_KEY=your_key_here" > .env

# Frontend
cd ../skillsync-frontend
npm install
```

#### Run

```bash
# Backend (from skillsync-backend/)
python -m uvicorn src.main:app --reload --port 8000

# Frontend (from skillsync-frontend/) — in a separate terminal
npm run dev
# Runs on http://localhost:3001
```

---

## Project Documentation

### Screenshots

#### 1. AI Call — Worker Onboarding (Malayalam)
![AI Call Interface](docs/ai_call.png)
*Voice-first onboarding: AI asks questions in the worker's native language (Malayalam shown). Worker speaks answers — system translates to English, shows confirmation screen with Confirm / Re-record / Edit options.*

#### 2. Worker Search — Distance Sorted with Filters
![Worker Search](docs/worker_search.png)
*Customer sees workers sorted by distance with Trust Score badges (Green/Yellow/Red), skill tags, rate, and distance shown. Advanced filter panel: skill, distance, price range, min Trust Score.*

#### 3. Worker Detail — Call Interface
![Call UI](docs/worker_call.png)
*In-app call flow: idle → ringing (ripple animation) → connected (live timer + sound wave + controls) → ended. Post-call review appears automatically after the call.*

#### 4. Worker Detail — Post-Call & Work Review
![Reviews](docs/reviews.png)
*Two review types: Call Review (auto-prompted after call ends) and Work Review (star rating + quick tags like "On time", "Professional" + written review). Both submitted to the verified ledger.*

#### 5. Customer Dashboard
![Customer Dashboard](docs/customer_dashboard.png)
*Customer home with geolocation, recent jobs, and quick access to worker search by skill category.*

---

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SKILLSYNC ARCHITECTURE                   │
├────────────────┬────────────────────────┬───────────────────────┤
│   FRONTEND     │      BACKEND (API)     │     SERVICES          │
│  React + Vite  │     FastAPI / Python   │                       │
│  Tailwind CSS  │                        │  Google Gemini AI     │
│  Vercel        │  ┌─ /api/auth          │  (Profile Extraction) │
│                │  ├─ /api/workers       │                       │
│  Pages:        │  ├─ /api/customers     │  gTTS                 │
│  - Landing     │  ├─ /api/jobs          │  (Multilingual TTS)   │
│  - Login       │  ├─ /api/reviews       │                       │
│  - WorkerSearch│  ├─ /api/calls         │  deep-translator      │
│  - WorkerDetail│  ├─ /api/emergency     │  (Auto Translation)   │
│  - AICallPage  │  └─ /api/ai-call       │                       │
│  - Dashboards  │                        │  Web Speech API       │
│                │  SQLAlchemy ORM        │  (STT in browser)     │
│  Axios → API   │  SQLite / PostgreSQL   │                       │
└────────────────┴────────────────────────┴───────────────────────┘
```

**Data Flow — Worker Onboarding:**
```
Worker speaks → Web Speech API (STT) → /api/ai-call/translate → English text shown
→ Worker confirms → Answers stored → /api/ai-call/extract-profile (Gemini NLP)
→ Structured profile JSON → /api/ai-call/save-profile → DB saved
→ Trust Score calculated → Profile live
```

**Data Flow — Aadhaar OTP:**
```
Worker speaks last 4 Aadhaar digits → /api/ai-call/generate-otp
→ OTP stored in server memory (5 min TTL) → Sent to worker
→ Worker speaks OTP → /api/ai-call/verify-otp → Identity Verified ✓
```

---

## API Documentation

**Base URL (Production):** `https://skillsync-backend.onrender.com`  
**Base URL (Local):** `http://localhost:8000`

All endpoints are prefixed with `/api`.

---

### Auth

**POST `/api/auth/send-otp`**
```json
{ "phone": "9876543210" }
```
**POST `/api/auth/verify-otp`**
```json
{ "phone": "9876543210", "otp": "123456" }
```
**POST `/api/auth/customer/register`**
```json
{ "phone": "9876543210", "name": "Priya Sharma", "location_lat": 12.97, "location_lng": 77.59 }
```

---

### Workers

**GET `/api/workers/search`**
- Params: `skill`, `lat`, `lng`, `radius_km`, `min_trust_score`, `max_daily_rate`, `language`
- Returns workers sorted by distance ascending

**GET `/api/workers/{worker_id}`**
- Full worker profile with photos, reviews, Trust Score

**POST `/api/workers/{worker_id}/photos`**
- Multipart form: `photos[]` (up to 10 images)

**GET `/api/workers/{worker_id}/trust-score`**
- Returns `total_score`, `score_breakdown`, `badge_color`

---

### AI Call (Voice Onboarding)

**POST `/api/ai-call/tts`**
```json
{ "text": "നിങ്ങളുടെ പേര് എന്താണ്?", "language": "Malayalam" }
```
Returns: `audio/mpeg` stream (gTTS generated)

**POST `/api/ai-call/translate`**
```json
{ "text": "എന്റെ പേര് രാജു", "source_language": "Malayalam" }
```
Returns: `{ "translated": "My name is Raju", "original": "..." }`

**POST `/api/ai-call/questions`**
```json
{ "phone": "9876543210", "language_key": "5" }
```
Returns: Array of 8 questions in the selected language

**POST `/api/ai-call/extract-profile`**
```json
{ "answers": { "name": "Raju", "skill": "Electrician", "experience": "10 years", ... }, "language": "Malayalam" }
```
Returns: Structured profile JSON (Gemini-extracted)

**POST `/api/ai-call/save-profile?phone=9876543210`**
Saves extracted profile to DB, triggers Trust Score calculation

**POST `/api/ai-call/generate-otp`**
```json
{ "phone": "9876543210", "aadhaar_last4": "4521" }
```
Generates and stores OTP (demo: returned in response for testing)

**POST `/api/ai-call/verify-otp`**
```json
{ "phone": "9876543210", "otp": "847291" }
```
Returns: `{ "verified": true }` or 400 error

---

### Reviews

**POST `/api/reviews/submit`**
```json
{
  "worker_id": "uuid",
  "customer_id": "uuid",
  "rating": 5,
  "review_text": "Excellent work, very professional",
  "review_type": "work",
  "tags": ["On time", "Professional"]
}
```

---

### Emergency

**POST `/api/emergency/trigger`**
```json
{
  "customer_id": "uuid",
  "worker_id": "uuid",
  "location_lat": 12.97,
  "location_lng": 77.59
}
```
Creates incident, flags worker, returns nearest police station info.

---

### Jobs

**POST `/api/jobs/create`**
```json
{ "worker_id": "uuid", "description": "Leaking pipe under kitchen sink" }
```

**POST `/api/jobs/{job_id}/respond`**
```json
{ "action": "accept" }
```

**GET `/api/jobs/qr/{qr_id}`**
Validates QR code for work ledger signoff

---

## AI Tools Used

**Tool Used:** GitHub Copilot (Claude Sonnet 4.6)

**Purpose:**
- Full-stack code generation — FastAPI backend, React frontend
- Debugging async functions, import errors, CORS configuration
- Multilingual AI call flow architecture
- Deployment configuration (Render + Vercel)
- Real-time fixes for Python 3.14 / SQLAlchemy compatibility on Render

**Key Features Built with AI Assistance:**
- Voice-first onboarding flow with 8-question AI interview
- Aadhaar OTP verification during live call
- Multilingual TTS pipeline (gTTS + deep-translator)
- Distance-sorted worker search with advanced filters
- In-app calling UI with ringing → connected → ended states
- Trust Score engine with weighted components
- Emergency button with GPS + auto-call protocol

**Percentage of AI-assisted code:** ~70%

**Human Contributions:**
- Problem definition and solution architecture
- UI/UX design decisions and visual language
- Feature prioritization for hackathon scope
- Testing, QA, and real-world scenario validation
- Business model and social impact framing

---

## Team Contributions

- **Amritha:** Full-stack development, AI/NLP pipeline, voice onboarding, deployment, UI/UX

---

## License

This project is licensed under the MIT License.

---

<p align="center">Made with ❤️ at TinkerHub Hackathon 2026</p>
<p align="center">
  <strong>SkillSync — Because every skilled hand deserves to be seen.</strong>
</p>
