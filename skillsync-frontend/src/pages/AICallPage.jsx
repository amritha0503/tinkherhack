import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getQuestions, extractProfile, saveProfile, transcribeVoice } from '../services/api'
import toast from 'react-hot-toast'

const LANGUAGES = [
  { key: '1', name: 'Malayalam', script: 'മലയാളം' },
  { key: '2', name: 'Hindi',     script: 'हिंदी' },
  { key: '3', name: 'Tamil',     script: 'தமிழ்' },
  { key: '4', name: 'Telugu',    script: 'తెలుగు' },
  { key: '5', name: 'Bengali',   script: 'বাংলা' },
  { key: '6', name: 'Marathi',   script: 'मराठी' },
  { key: '7', name: 'Kannada',   script: 'ಕನ್ನಡ' },
  { key: '8', name: 'English',   script: 'English' },
]

const IVR_LINES = [
  'Welcome to SkillSync — the worker profile platform.',
  '',
  'To continue in your language, press a number:',
  '',
  '  1 → Malayalam  (മലയാളം)',
  '  2 → Hindi      (हिंदी)',
  '  3 → Tamil      (தமிழ்)',
  '  4 → Telugu     (తెలుగు)',
  '  5 → Bengali    (বাংলা)',
  '  6 → Marathi    (मराठी)',
  '  7 → Kannada    (ಕನ್ನಡ)',
  '  8 → English',
  '',
  'Press your number now.',
]

function useTimer(active) {
  const [secs, setSecs] = useState(0)
  useEffect(() => {
    if (!active) { setSecs(0); return }
    const t = setInterval(() => setSecs(s => s + 1), 1000)
    return () => clearInterval(t)
  }, [active])
  const mm = String(Math.floor(secs / 60)).padStart(2, '0')
  const ss = String(secs % 60).padStart(2, '0')
  return mm + ':' + ss
}

export default function AICallPage() {
  const navigate    = useNavigate()
  const [stage, setStage]       = useState('dial')
  const [phone, setPhone]       = useState('')
  const [langKey, setLangKey]   = useState('')
  const [language, setLang]     = useState('')
  const [greeting, setGreeting] = useState('')
  const [questions, setQs]      = useState([])
  const [current, setCurrent]   = useState(0)
  const [answers, setAnswers]   = useState({})
  const [answer, setAnswer]     = useState('')
  const [profile, setProfile]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [isRecording, setRec]   = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const [ivrLine, setIvrLine]   = useState(0)
  const [showKeys, setShowKeys] = useState(false)
  const [ivrMsg, setIvrMsg]     = useState('')
  const mediaRef  = useRef(null)
  const chunksRef = useRef([])
  const answerRef = useRef(null)

  const callActive = ['ivr','interview','reviewing'].includes(stage)
  const timer = useTimer(callActive)

  // IVR typewriter effect
  useEffect(() => {
    if (stage !== 'ivr') return
    setIvrLine(0)
    setShowKeys(false)
    setIvrMsg('')
    let line = 0
    const interval = setInterval(() => {
      if (line < IVR_LINES.length) {
        setIvrMsg(prev => prev + IVR_LINES[line] + '\n')
        line++
      } else {
        clearInterval(interval)
        setShowKeys(true)
      }
    }, 180)
    return () => clearInterval(interval)
  }, [stage])

  // Keyboard shortcut for language selection
  useEffect(() => {
    if (stage !== 'ivr' || !showKeys) return
    function onKey(e) {
      if ('12345678'.includes(e.key)) handleLangKey(e.key)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [stage, showKeys])

  async function handleCall() {
    const digits = phone.replace(/\D/g, '')
    if (digits.length < 10) { toast.error('Enter a valid 10-digit number'); return }
    setStage('ringing')
    await new Promise(r => setTimeout(r, 3000))
    setStage('ivr')
  }

  async function handleLangKey(k) {
    if (loading) return
    const lang = LANGUAGES.find(l => l.key === k)
    if (!lang) return
    setLangKey(k)
    setLang(lang.name)
    setShowKeys(false)
    setIvrMsg('You selected ' + lang.name + ' (' + lang.script + ').\n\nConnecting you to interview questions in ' + lang.name + '...\n\nPlease hold.')
    setLoading(true)
    try {
      const res = await getQuestions(phone.replace(/\D/g,''), k)
      setGreeting(res.data.greeting || '')
      setQs(res.data.questions || [])
      setCurrent(0)
      setAnswers({})
      setAnswer('')
      setStage('interview')
    } catch {
      toast.error('Backend error — is the server running on port 8000?')
      setStage('ivr')
      setShowKeys(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (stage === 'interview' && questions[current]) {
      setAnswer('')
      setTimeout(() => answerRef.current?.focus(), 100)
    }
  }, [current, stage])

  function handleAnswer() {
    if (!answer.trim()) { toast.error('Please type your answer'); return }
    const q = questions[current]
    const updated = { ...answers, [q.key]: answer.trim() }
    setAnswers(updated)
    if (current + 1 < questions.length) {
      setCurrent(c => c + 1)
    } else {
      doExtract(updated)
    }
  }

  async function doExtract(finalAnswers) {
    setStage('reviewing')
    setLoading(true)
    try {
      const res = await extractProfile({ phone: phone.replace(/\D/g,''), language, answers: finalAnswers })
      setProfile(res.data.profile)
    } catch {
      setProfile({ name: finalAnswers.name, skill_type: finalAnswers.skill, bio_english: finalAnswers.about })
    }
    setLoading(false)
    setStage('done')
  }

  async function handleSave() {
    setLoading(true)
    try {
      await saveProfile(phone.replace(/\D/g,''), profile)
      toast.success('Profile saved! Worker is now discoverable by customers.')
      setTimeout(() => navigate('/search'), 1500)
    } catch {
      toast.error('Save failed')
    } finally { setLoading(false) }
  }

  function endCall() {
    setStage('dial'); setPhone(''); setLangKey(''); setQs([]); setAnswers({}); setProfile(null)
  }

  async function toggleRecording() {
    if (isRecording) {
      // Stop recording — this triggers onstop which uploads + transcribes
      mediaRef.current?.stop()
      setRec(false)
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // Pick best supported format
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/ogg'
      const rec = new MediaRecorder(stream, { mimeType })
      mediaRef.current = rec
      chunksRef.current = []
      rec.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data) }
      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunksRef.current, { type: mimeType })
        if (blob.size < 1000) {
          toast.error('Recording too short — please speak longer')
          return
        }
        // Send to backend for transcription
        const currentQ = questions[current]
        if (!currentQ) return
        setTranscribing(true)
        try {
          const res = await transcribeVoice(
            phone.replace(/\D/g, ''),
            language,
            currentQ.key,
            blob
          )
          const text = res.data?.transcript || ''
          if (text) {
            setAnswer(text)
            toast.success('Voice transcribed — review and confirm')
          } else {
            toast.error('Could not transcribe — please type your answer')
          }
        } catch (err) {
          const msg = err?.response?.data?.detail || 'Transcription failed'
          toast.error(msg + ' — type your answer instead')
        } finally {
          setTranscribing(false)
        }
      }
      rec.start(100) // collect data every 100ms
      setRec(true)
      toast('🎙 Recording started — speak now', { duration: 2000 })
    } catch {
      toast.error('Microphone access denied')
    }
  }

  // Phone call frame wrapper
  const PhoneFrame = ({ children }) => (
    <div className="w-full max-w-sm mx-auto">
      <div className="bg-gray-900 rounded-3xl border-2 border-gray-700 shadow-2xl overflow-hidden">
        <div className="bg-green-700 px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 bg-green-300 rounded-full animate-pulse" />
            <span className="text-green-100 text-xs font-bold tracking-widest">CALL CONNECTED</span>
          </div>
          <span className="text-green-200 text-xs font-mono font-semibold">{timer}</span>
        </div>
        <div className="bg-gray-800 px-5 py-3 flex items-center gap-3 border-b border-gray-700">
          <div className="w-9 h-9 bg-indigo-600 rounded-full flex items-center justify-center text-base font-black">S</div>
          <div>
            <p className="text-white text-sm font-bold">SkillSync AI Agent</p>
            <p className="text-gray-400 text-xs">+91 {phone.replace(/\D/g,'')}</p>
          </div>
        </div>
        <div className="min-h-64 px-5 py-5">{children}</div>
        <div className="px-5 pb-5 pt-2 border-t border-gray-700 flex justify-center">
          <button onClick={endCall} title="End Call"
            className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-xl hover:bg-red-500 transition-colors shadow-lg">
            📵
          </button>
        </div>
      </div>
      <p className="text-center text-xs text-gray-600 mt-2">Tap 📵 to end call</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <nav className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <button onClick={() => navigate('/')} className="flex items-center gap-1">
          <span className="text-xl font-black text-indigo-400">Skill</span>
          <span className="text-xl font-black text-white">Sync</span>
        </button>
        <span className="text-xs text-gray-500 bg-gray-800 px-3 py-1 rounded-full">AI Worker Onboarding Call</span>
      </nav>

      <div className="flex-1 flex items-center justify-center px-4 py-10">

        {/* DIAL SCREEN */}
        {stage === 'dial' && (
          <div className="w-full max-w-sm mx-auto">
            <div className="bg-gray-900 rounded-3xl border-2 border-gray-700 shadow-2xl overflow-hidden">
              <div className="bg-gray-800 px-6 pt-8 pb-5 text-center border-b border-gray-700">
                <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center text-3xl font-black mx-auto mb-3">S</div>
                <p className="text-white font-bold">SkillSync AI Agent</p>
                <p className="text-gray-400 text-xs mt-0.5">Worker Onboarding • Multilingual</p>
              </div>
              <div className="px-6 py-5">
                <label className="block text-xs text-gray-500 mb-2 uppercase tracking-wide">Worker Phone Number</label>
                <div className="flex items-center bg-gray-800 border border-gray-700 rounded-xl overflow-hidden mb-4">
                  <span className="text-gray-400 text-sm px-3 border-r border-gray-700 py-3">+91</span>
                  <input type="tel" value={phone}
                    onChange={e => setPhone(e.target.value.replace(/\D/g,'').slice(0,10))}
                    placeholder="Enter 10-digit number" maxLength={10}
                    className="flex-1 bg-transparent px-3 py-3 text-white text-sm focus:outline-none placeholder-gray-600"
                    onKeyDown={e => e.key === 'Enter' && handleCall()} />
                </div>
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {['1','2','3','4','5','6','7','8','9','*','0','#'].map(d => (
                    <button key={d}
                      onClick={() => !'*#'.includes(d) && setPhone(p => (p + d).slice(0,10))}
                      className="bg-gray-800 border border-gray-700 rounded-xl py-3 text-white text-sm font-semibold hover:bg-gray-700 active:scale-95 transition-all">
                      {d}
                    </button>
                  ))}
                </div>
                <button onClick={handleCall} disabled={phone.replace(/\D/g,'').length < 10}
                  className="w-full bg-green-600 text-white font-bold py-3.5 rounded-xl hover:bg-green-500 disabled:opacity-40 transition-colors flex items-center justify-center gap-2 text-sm">
                  <span>📞</span> Call Worker
                </button>
              </div>
            </div>
            <p className="text-center text-xs text-gray-600 mt-3">AI will ask worker to select language using keypad</p>
          </div>
        )}

        {/* RINGING */}
        {stage === 'ringing' && (
          <div className="w-full max-w-sm mx-auto">
            <div className="bg-gray-900 rounded-3xl border-2 border-gray-700 shadow-2xl overflow-hidden">
              <div className="px-6 py-12 text-center">
                <div className="relative mx-auto w-24 h-24 mb-6">
                  <div className="absolute inset-0 bg-green-500 rounded-full opacity-20 animate-ping" />
                  <div className="absolute inset-3 bg-green-500 rounded-full opacity-25 animate-ping" style={{animationDelay:'0.4s'}} />
                  <div className="relative w-24 h-24 bg-indigo-600 rounded-full flex items-center justify-center text-4xl font-black">S</div>
                </div>
                <p className="text-white font-bold text-lg">SkillSync AI Agent</p>
                <p className="text-gray-400 text-sm mt-1">Calling +91 {phone.replace(/\D/g,'')}...</p>
                <div className="flex justify-center gap-2 mt-5">
                  {[0,0.25,0.5].map(d => (
                    <div key={d} className="w-2.5 h-2.5 bg-green-400 rounded-full animate-bounce" style={{animationDelay:d+'s'}} />
                  ))}
                </div>
              </div>
              <div className="px-6 pb-6 flex justify-center border-t border-gray-700 pt-4">
                <button onClick={endCall} className="w-13 h-13 w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-xl hover:bg-red-500">📵</button>
              </div>
            </div>
          </div>
        )}

        {/* IVR: LANGUAGE SELECTION */}
        {stage === 'ivr' && (
          <PhoneFrame>
            <div className="font-mono text-sm text-green-300 whitespace-pre leading-relaxed min-h-44">
              {ivrMsg}
              {!showKeys && <span className="inline-block w-2 h-4 bg-green-400 ml-0.5 animate-pulse align-middle" />}
            </div>
            {showKeys && (
              <div className="mt-3">
                <p className="text-xs text-gray-500 mb-2">Tap a number or press keyboard:</p>
                <div className="grid grid-cols-4 gap-1.5">
                  {LANGUAGES.map(l => (
                    <button key={l.key} onClick={() => handleLangKey(l.key)}
                      className="bg-gray-700 hover:bg-indigo-700 border border-gray-600 hover:border-indigo-500 rounded-xl py-2 text-center transition-all active:scale-95 disabled:opacity-50"
                      disabled={loading}>
                      <div className="text-white font-bold text-base">{l.key}</div>
                      <div className="text-gray-400 text-xs mt-0.5 leading-tight">{l.name.slice(0,4)}</div>
                    </button>
                  ))}
                </div>
                {loading && (
                  <div className="mt-3 flex items-center gap-2 text-yellow-400 text-xs">
                    <div className="w-3 h-3 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
                    Loading {language} questions...
                  </div>
                )}
              </div>
            )}
          </PhoneFrame>
        )}

        {/* INTERVIEW */}
        {stage === 'interview' && questions.length > 0 && (
          <PhoneFrame>
            <div className="flex gap-0.5 mb-4">
              {questions.map((_, i) => (
                <div key={i} className={'h-1 flex-1 rounded-full transition-all ' + (i < current ? 'bg-green-500' : i === current ? 'bg-indigo-400' : 'bg-gray-700')} />
              ))}
            </div>
            {current === 0 && greeting && (
              <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 mb-3 text-xs text-gray-300 italic">
                🤖 {greeting}
              </div>
            )}
            <div className="flex items-start gap-2 mb-3">
              <div className="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">AI</div>
              <div className="bg-gray-800 rounded-2xl rounded-tl-none px-3 py-2 text-sm text-gray-100 leading-relaxed flex-1">
                {questions[current].question}
              </div>
            </div>
            <textarea ref={answerRef} value={answer} onChange={e => setAnswer(e.target.value)}
              placeholder="Type your answer..." rows={3}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-gray-600 resize-none"
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAnswer() } }} />
            <div className="flex gap-2 mt-2">
              <button onClick={toggleRecording} disabled={transcribing}
                className={'px-3 py-2 rounded-lg text-xs font-semibold transition-all border ' + (isRecording ? 'bg-red-600 text-white border-red-600 animate-pulse' : transcribing ? 'bg-yellow-700 text-yellow-200 border-yellow-600 animate-pulse' : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600')}>
                {isRecording ? '⏹ Stop' : transcribing ? '⏳ Transcribing...' : '🎙 Voice'}
              </button>
              <button onClick={handleAnswer}
                className="flex-1 bg-indigo-600 text-white text-xs font-bold py-2 rounded-lg hover:bg-indigo-500 transition-colors">
                {current + 1 < questions.length ? 'Next (' + (current+1) + '/' + questions.length + ') →' : 'Finish ✓'}
              </button>
            </div>
          </PhoneFrame>
        )}

        {/* REVIEWING */}
        {stage === 'reviewing' && (
          <PhoneFrame>
            <div className="text-center py-8">
              <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-white font-bold text-sm">Analysing your answers...</p>
              <p className="text-gray-400 text-xs mt-2">Gemini AI is building your worker profile</p>
            </div>
          </PhoneFrame>
        )}

        {/* DONE */}
        {stage === 'done' && profile && (
          <div className="w-full max-w-sm mx-auto">
            <div className="bg-gray-900 rounded-3xl border-2 border-gray-700 shadow-2xl overflow-hidden">
              <div className="bg-indigo-700 px-5 py-4 flex items-center gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <p className="text-white font-bold text-sm">Call Complete</p>
                  <p className="text-indigo-200 text-xs">AI-built profile ready</p>
                </div>
              </div>
              <div className="px-5 py-5 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-indigo-600 rounded-full flex items-center justify-center text-xl font-black">
                    {(profile.name || 'W')[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="text-white font-bold">{profile.name || 'Worker'}</p>
                    <p className="text-gray-400 text-xs">{profile.skill_type} · {language}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {[
                    ['Experience', profile.experience_years ? profile.experience_years + ' yrs' : null],
                    ['Daily Rate',  profile.daily_rate ? '₹' + profile.daily_rate + '/day' : null],
                    ['Location',   profile.location_hint],
                    ['Skills',     profile.specializations?.join(', ')],
                  ].filter(r => r[1]).map(([k,v]) => (
                    <div key={k} className="bg-gray-800 rounded-lg p-2.5">
                      <p className="text-gray-500 uppercase tracking-wide text-xs">{k}</p>
                      <p className="text-white font-semibold mt-0.5">{v}</p>
                    </div>
                  ))}
                </div>
                {profile.bio_english && (
                  <div className="bg-gray-800 rounded-lg p-3">
                    <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">AI Bio</p>
                    <p className="text-gray-300 text-xs leading-relaxed italic">"{profile.bio_english}"</p>
                  </div>
                )}
                <div className="flex gap-2 pt-1">
                  <button onClick={handleSave} disabled={loading}
                    className="flex-1 bg-green-600 text-white font-bold py-3 rounded-xl hover:bg-green-500 disabled:opacity-50 text-sm transition-colors">
                    {loading ? 'Saving...' : '💾 Save Profile'}
                  </button>
                  <button onClick={endCall}
                    className="px-4 bg-gray-700 text-gray-300 font-bold py-3 rounded-xl hover:bg-gray-600 text-sm">
                    New
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
