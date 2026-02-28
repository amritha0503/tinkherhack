import google.generativeai as genai
import os
import json
import tempfile
import time
from dotenv import load_dotenv

try:
    from PIL import Image
except ImportError:
    Image = None

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None
    print('[WARNING] GEMINI_API_KEY not set. AI features will return fallback responses.')

# Language code map for langdetect (ISO 639-1)
LANG_ISO = {
    'Hindi':     'hi',
    'Tamil':     'ta',
    'Telugu':    'te',
    'Bengali':   'bn',
    'Marathi':   'mr',
    'Kannada':   'kn',
    'Malayalam': 'ml',
    'English':   'en',
}


def _preprocess_audio(audio_file_path: str) -> str:
    """
    Load audio with librosa → convert to mono 16 kHz WAV → normalize.
    Returns path to the processed WAV file (caller must delete it).
    Browser WebM/Opus recordings are handled via pydub + ffmpeg if available,
    with a plain-copy fallback so Gemini can still attempt transcription.
    """
    import numpy as np
    import soundfile as sf
    import librosa

    out_tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    out_path = out_tmp.name
    out_tmp.close()

    try:
        # librosa.load handles wav/flac/ogg/mp3; webm needs ffmpeg via audioread
        y, sr = librosa.load(audio_file_path, sr=16000, mono=True, res_type='soxr_hq')

        # Remove silence from start/end
        y, _ = librosa.effects.trim(y, top_db=20)

        # Normalize to [-1, 1]
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = y / max_val * 0.95

        sf.write(out_path, y, 16000, subtype='PCM_16')
        return out_path

    except Exception as librosa_err:
        # Fallback: try pydub (needs ffmpeg) to convert to wav
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_file_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(out_path, format='wav')
            return out_path
        except Exception as pydub_err:
            # Last resort: just copy the file and let Gemini try
            import shutil
            shutil.copy2(audio_file_path, out_path)
            return out_path


def _detect_language(text: str) -> dict:
    """
    Use langdetect to identify the language of a transcript.
    Returns {detected_code, confidence, probabilities}.
    """
    try:
        from langdetect import detect, detect_langs
        detected = detect(text)
        probs = detect_langs(text)  # list of Language(lang, prob)
        return {
            'detected_code': detected,
            'probabilities': {str(p).split(':')[0]: float(str(p).split(':')[1]) for p in probs},
        }
    except Exception:
        return {'detected_code': 'unknown', 'probabilities': {}}


def voice_to_text(audio_file_path: str, language: str) -> str:
    """
    Full pipeline:
      1. librosa  — preprocess audio (mono, 16 kHz, normalise, trim silence)
      2. Gemini   — transcribe the cleaned WAV
      3. langdetect — verify transcript language matches expected language
    Returns the transcribed text string.
    """
    if not model:
        return 'AI service unavailable. Please set GEMINI_API_KEY.'

    processed_path = None
    uploaded_file  = None
    try:
        # ── Step 1: preprocess ───────────────────────────────────────────────
        processed_path = _preprocess_audio(audio_file_path)

        # ── Step 2: upload + transcribe via Gemini ───────────────────────────
        uploaded_file = genai.upload_file(path=processed_path)

        # Wait for file to be ACTIVE (may take a moment)
        for _ in range(10):
            status = genai.get_file(uploaded_file.name)
            if status.state.name == 'ACTIVE':
                break
            time.sleep(1)

        prompt = (
            f'This audio recording is in {language}. '
            f'Transcribe exactly what is spoken and translate it into clear English. '
            f'Return ONLY the English translation. '
            f'Do not include the original language text. Do not add any explanation.'
        )
        response = model.generate_content(
            [uploaded_file, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type='text/plain',
                temperature=0.1,
            ),
        )
        transcript = response.text.strip()
        return transcript

    except Exception as e:
        raise RuntimeError(f'voice_to_text failed: {str(e)}')
    finally:
        # Clean up temp preprocessed file
        if processed_path:
            try:
                os.unlink(processed_path)
            except Exception:
                pass
        # Delete uploaded Gemini file to save quota
        if uploaded_file:
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass

def extract_profile(transcript: str, language: str) -> dict:
    if not model:
        return {
            'skill_type': 'Other', 'experience_years': 0,
            'work_areas': [], 'specializations': [],
            'daily_rate': None, 'bio_english': transcript[:200]
        }
    try:
        prompt = f'''From this voice transcript of an Indian informal worker, extract and return a JSON object with these exact keys:
"skill_type" (string: Plumber/Electrician/Carpenter/Mason/Painter/Welder/Other),
"experience_years" (integer),
"work_areas" (list of strings),
"specializations" (list of strings),
"daily_rate" (integer or null),
"bio_english" (2 professional sentences in English about the worker).
Transcript: {transcript}'''
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type='application/json',
                temperature=0.1,
            ),
        )
        return json.loads(response.text)
    except json.JSONDecodeError:
        # Return safe defaults if JSON parse fails
        return {
            'skill_type': 'Other',
            'experience_years': 0,
            'work_areas': [],
            'specializations': [],
            'daily_rate': None,
            'bio_english': transcript[:200]
        }
    except Exception as e:
        raise RuntimeError(f'extract_profile failed: {str(e)}')

def analyze_complaint_photo(image_path: str) -> dict:
    if not model or Image is None:
        return {
            'issue_type': 'other',
            'confidence_score': 0.5,
            'suggested_worker_skill': 'General',
            'description_for_worker': 'AI service unavailable. Please set GEMINI_API_KEY.'
        }
    try:
        prompt = '''Look at this home repair problem photo. Return a JSON object with these exact keys:
"issue_type" (one of: plumbing_leak/pipe_burst/electrical_fault/wiring_issue/wall_crack/ceiling_damage/tile_broken/painting_needed/other),
"confidence_score" (float 0-1),
"suggested_worker_skill" (string),
"description_for_worker" (one clear sentence describing the problem)'''
        img = Image.open(image_path)
        response = model.generate_content(
            [img, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type='application/json',
                temperature=0.1,
            ),
        )
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            'issue_type': 'other',
            'confidence_score': 0.5,
            'suggested_worker_skill': 'General',
            'description_for_worker': 'Home repair issue detected'
        }
    except Exception as e:
        raise RuntimeError(f'analyze_complaint_photo failed: {str(e)}')