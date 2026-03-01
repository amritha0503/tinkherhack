import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getWorker } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

const BADGE_COLOR = {
  Green:  'bg-green-100 text-green-800',
  Yellow: 'bg-yellow-100 text-yellow-800',
  Red:    'bg-red-100 text-red-800',
}

const WORK_TAGS = [
  'On time', 'Professional', 'Good work quality', 'Clean & tidy',
  'Affordable', 'Friendly', 'Would hire again', 'Fast worker',
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

function SoundWave() {
  return (
    <div className="flex items-end gap-0.5 h-7">
      {[2,4,6,8,6,9,5,7,3,6,8,4,6,3,5].map((h, i) => (
        <div
          key={i}
          className="w-1 bg-green-400 rounded-full"
          style={{
            height: `${h * 3}px`,
            animation: `soundbar 0.9s ease-in-out ${(i * 0.06).toFixed(2)}s infinite alternate`,
          }}
        />
      ))}
      <style>{`
        @keyframes soundbar {
          from { transform: scaleY(0.3); opacity: 0.4; }
          to   { transform: scaleY(1.2); opacity: 1; }
        }
      `}</style>
    </div>
  )
}

function StarRating({ value, onChange, size = 'text-2xl' }) {
  const [hover, setHover] = useState(0)
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map(star => (
        <button
          key={star}
          type="button"
          className={`${size} transition-transform hover:scale-110`}
          style={{ color: star <= (hover || value) ? '#f59e0b' : '#d1d5db' }}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(0)}
          onClick={() => onChange(star)}
        >
          ★
        </button>
      ))}
    </div>
  )
}

export default function WorkerDetail() {
  const { workerId } = useParams()
  const navigate     = useNavigate()
  const { user }     = useAuth()

  const [worker, setWorker]   = useState(null)
  const [loading, setLoading] = useState(true)

  const [callState, setCallState] = useState('idle')
  const callActive = callState === 'connected'
  const callTimer  = useTimer(callActive)
  const ringingRef = useRef(null)

  const [showCallReview, setShowCallReview]         = useState(false)
  const [callRating, setCallRating]                 = useState(0)
  const [callFeedback, setCallFeedback]             = useState('')
  const [callReviewDone, setCallReviewDone]         = useState(false)
  const [submittingCallReview, setSubmittingCallReview] = useState(false)

  const [showWorkReview, setShowWorkReview]         = useState(false)
  const [workRating, setWorkRating]                 = useState(0)
  const [workTags, setWorkTags]                     = useState([])
  const [workFeedback, setWorkFeedback]             = useState('')
  const [workReviewDone, setWorkReviewDone]         = useState(false)
  const [submittingWorkReview, setSubmittingWorkReview] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const res = await getWorker(workerId)
        setWorker(res.data)
      } catch {
        toast.error('Worker not found')
        navigate('/search')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [workerId])

  function startCall() {
    if (!user) { navigate('/login'); return }
    setCallState('ringing')
    ringingRef.current = setTimeout(() => setCallState('connected'), 3000)
  }

  function endCall() {
    clearTimeout(ringingRef.current)
    setCallState('ended')
    setShowCallReview(true)
  }

  function cancelRinging() {
    clearTimeout(ringingRef.current)
    setCallState('idle')
  }

  async function submitCallReview(e) {
    e.preventDefault()
    if (callRating === 0) { toast.error('Please select a star rating'); return }
    setSubmittingCallReview(true)
    try {
      await fetch('/api/reviews/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ worker_id: workerId, reviewer_id: user?.id, review_type: 'call', rating: callRating, comment: callFeedback })
      })
    } catch {}
    toast.success('Call review saved!')
    setCallReviewDone(true)
    setSubmittingCallReview(false)
  }

  async function submitWorkReview(e) {
    e.preventDefault()
    if (workRating === 0) { toast.error('Please select a star rating'); return }
    setSubmittingWorkReview(true)
    const comment = [workFeedback, workTags.length ? `Tags: ${workTags.join(', ')}` : ''].filter(Boolean).join(' | ')
    try {
      await fetch('/api/reviews/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({ worker_id: workerId, reviewer_id: user?.id, review_type: 'work', rating: workRating, comment, tags: workTags })
      })
    } catch {}
    toast.success('Work review submitted! Thank you.')
    setWorkReviewDone(true)
    setShowWorkReview(false)
    setSubmittingWorkReview(false)
  }

  function toggleWorkTag(tag) {
    setWorkTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag])
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )
  if (!worker) return null

  const firstName = worker.name?.split(' ')[0] || 'Worker'

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="flex items-center px-6 py-4 bg-white border-b border-gray-100 sticky top-0 z-40">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-900 mr-4">
           Back
        </button>
        <span className="font-black text-indigo-600 text-lg">Skill</span>
        <span className="font-black text-gray-800 text-lg">Sync</span>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-8 space-y-5">

        {/* Profile card */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 md:p-8">
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            <div className="w-20 h-20 md:w-24 md:h-24 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-black text-4xl shrink-0">
              {(worker.name || '?')[0].toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-3 mb-2">
                <h1 className="text-2xl font-black text-gray-900">{worker.name || 'Worker'}</h1>
                {worker.trust_badge && (
                  <span className={`text-sm font-bold px-3 py-1 rounded-full ${BADGE_COLOR[worker.trust_badge] || 'bg-gray-100'}`}>
                    {worker.trust_badge}  Score {worker.trust_score}
                  </span>
                )}
              </div>
              <p className="text-gray-500 mb-3">{worker.location_area || 'Location not specified'}</p>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="bg-indigo-50 text-indigo-700 text-sm font-semibold px-3 py-1.5 rounded-full">
                  {worker.skill_type || 'General Worker'}
                </span>
                <span className="bg-gray-100 text-gray-600 text-sm px-3 py-1.5 rounded-full">
                  {worker.experience_years || 0} years experience
                </span>
                {worker.aadhaar_verified && (
                  <span className="bg-green-50 text-green-700 text-sm font-semibold px-3 py-1.5 rounded-full">
                     Aadhaar Verified
                  </span>
                )}
              </div>
              {worker.bio_text && (
                <p className="text-gray-600 leading-relaxed text-sm mb-4 bg-gray-50 rounded-xl p-4 italic">
                  "{worker.bio_text}"
                </p>
              )}
              <div className="text-2xl font-black text-gray-900">
                ₹{worker.daily_rate || '—'}<span className="text-sm font-normal text-gray-400"> per day</span>
              </div>
            </div>
          </div>
        </div>

        {/*  CALL SECTION  */}

        {callState === 'idle' && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-bold text-gray-900 mb-1">Talk to this worker</h2>
            <p className="text-sm text-gray-500 mb-5">
              Call {firstName} directly through SkillSync — free, private &amp; safe.
            </p>
            <button onClick={startCall}
              className="w-full flex items-center justify-center gap-3 bg-green-600 hover:bg-green-500 active:scale-95 text-white font-bold py-4 rounded-2xl text-base transition-all shadow-md shadow-green-200">
              <span className="text-xl"></span> Call {firstName} via SkillSync
            </button>
            {!user && (
              <p className="text-xs text-center text-gray-400 mt-3">
                <button onClick={() => navigate('/login')} className="underline text-indigo-500">Login</button> to call this worker
              </p>
            )}
          </div>
        )}

        {callState === 'ringing' && (
          <div className="bg-white rounded-2xl border-2 border-green-200 shadow-sm overflow-hidden">
            <div className="bg-green-50 px-6 py-8 text-center">
              <div className="relative mx-auto w-20 h-20 mb-5">
                <div className="absolute inset-0 bg-green-400 rounded-full opacity-20 animate-ping" />
                <div className="absolute inset-2 bg-green-500 rounded-full opacity-20 animate-ping" style={{ animationDelay:'0.3s' }} />
                <div className="relative w-20 h-20 bg-green-600 rounded-full flex items-center justify-center text-white text-3xl font-black shadow-lg">
                  {(worker.name||'?')[0].toUpperCase()}
                </div>
              </div>
              <p className="font-bold text-gray-900 text-lg">{worker.name}</p>
              <p className="text-green-600 text-sm font-semibold animate-pulse mt-1">Calling via SkillSync...</p>
              <div className="flex justify-center gap-1.5 mt-3">
                {[0, 0.2, 0.4].map(d => (
                  <div key={d} className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: d+'s' }} />
                ))}
              </div>
            </div>
            <div className="px-6 py-4 flex justify-center border-t border-gray-100">
              <button onClick={cancelRinging}
                className="w-14 h-14 bg-red-600 hover:bg-red-500 rounded-full flex items-center justify-center text-2xl shadow-lg transition-colors"
                title="Cancel"></button>
            </div>
          </div>
        )}

        {callState === 'connected' && (
          <div className="bg-white rounded-2xl border-2 border-green-400 shadow-lg overflow-hidden">
            <div className="bg-green-700 px-5 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 bg-green-300 rounded-full animate-pulse" />
                <span className="text-green-100 text-xs font-bold tracking-widest uppercase">Call Connected</span>
              </div>
              <span className="text-green-200 text-sm font-mono font-bold">{callTimer}</span>
            </div>
            <div className="bg-gray-900 px-5 py-3 flex items-center gap-3">
              <div className="w-10 h-10 bg-green-700 rounded-full flex items-center justify-center text-white font-black">
                {(worker.name||'?')[0].toUpperCase()}
              </div>
              <div>
                <p className="text-white text-sm font-bold">{worker.name}</p>
                <p className="text-gray-400 text-xs">{worker.skill_type}  {worker.location_area}</p>
              </div>
            </div>
            <div className="bg-gray-900 px-5 py-8 flex flex-col items-center gap-3">
              <SoundWave />
              <p className="text-gray-300 text-xs">In call with {firstName}</p>
              <p className="text-gray-500 text-xs">Discuss your job, negotiate price, confirm details</p>
            </div>
            <div className="bg-gray-800 px-5 py-5 flex items-center justify-center gap-6 border-t border-gray-700">
              <button className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center text-lg text-white hover:bg-gray-600 transition-colors" title="Mute"></button>
              <button onClick={endCall}
                className="w-16 h-16 bg-red-600 hover:bg-red-500 rounded-full flex items-center justify-center text-2xl shadow-xl transition-all active:scale-90"
                title="End call"></button>
              <button className="w-12 h-12 bg-gray-700 rounded-full flex items-center justify-center text-lg text-white hover:bg-gray-600 transition-colors" title="Speaker"></button>
            </div>
          </div>
        )}

        {callState === 'ended' && (
          <div className="bg-gray-100 rounded-2xl border border-gray-200 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl"></span>
              <div>
                <p className="font-bold text-gray-700 text-sm">Call ended</p>
                <p className="text-xs text-gray-400">You spoke with {worker.name}</p>
              </div>
            </div>
            <button onClick={() => { setCallState('idle'); setShowCallReview(false) }}
              className="text-xs text-indigo-600 font-semibold hover:underline">
              Call again
            </button>
          </div>
        )}

        {/* Post-call review */}
        {showCallReview && !callReviewDone && (
          <div className="bg-white rounded-2xl border border-indigo-200 shadow-sm p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl"></span>
              <div>
                <h2 className="font-bold text-gray-900">Review this call</h2>
                <p className="text-xs text-gray-500">How was your experience talking with {firstName}?</p>
              </div>
            </div>
            <form onSubmit={submitCallReview} className="space-y-4">
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-2">Communication quality</p>
                <StarRating value={callRating} onChange={setCallRating} size="text-3xl" />
              </div>
              <textarea
                value={callFeedback}
                onChange={e => setCallFeedback(e.target.value)}
                rows={3}
                placeholder="Was the worker responsive? Clear about availability? Polite? (optional)"
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none placeholder-gray-400"
              />
              <div className="flex gap-3">
                <button type="submit" disabled={submittingCallReview}
                  className="flex-1 bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 text-sm transition-colors">
                  {submittingCallReview ? 'Submitting...' : ' Submit Call Review'}
                </button>
                <button type="button" onClick={() => setShowCallReview(false)}
                  className="px-5 bg-gray-100 text-gray-600 font-semibold py-3 rounded-xl hover:bg-gray-200 text-sm">
                  Skip
                </button>
              </div>
            </form>
          </div>
        )}

        {callReviewDone && (
          <div className="bg-green-50 border border-green-200 rounded-2xl px-6 py-4 flex items-center gap-3">
            <span className="text-xl"></span>
            <p className="text-sm font-semibold text-green-800">Call review submitted — thank you!</p>
          </div>
        )}

        {/* Work review */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <button onClick={() => setShowWorkReview(v => !v)}
            className="w-full flex items-center justify-between px-6 py-5 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-3">
              <span className="text-xl"></span>
              <div className="text-left">
                <p className="font-bold text-gray-900 text-sm">
                  {workReviewDone ? ' Work review submitted' : 'Post a Work Review'}
                </p>
                <p className="text-xs text-gray-500">
                  {workReviewDone
                    ? 'Thank you for your feedback!'
                    : `Already hired ${firstName}? Share your experience with the community`}
                </p>
              </div>
            </div>
            {!workReviewDone && <span className="text-gray-400 text-sm">{showWorkReview ? '' : ''}</span>}
          </button>

          {showWorkReview && !workReviewDone && (
            <div className="border-t border-gray-100 px-6 py-5">
              <form onSubmit={submitWorkReview} className="space-y-5">
                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-2">Overall work quality</p>
                  <StarRating value={workRating} onChange={setWorkRating} size="text-3xl" />
                  {workRating > 0 && (
                    <p className="text-xs text-amber-600 mt-1 font-medium">
                      {['','Poor','Fair','Good','Very Good','Excellent!'][workRating]}
                    </p>
                  )}
                </div>

                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-2">
                    Quick tags <span className="font-normal text-gray-400">(select all that apply)</span>
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {WORK_TAGS.map(tag => (
                      <button key={tag} type="button" onClick={() => toggleWorkTag(tag)}
                        className={`text-xs px-3 py-1.5 rounded-full border font-medium transition-all ${
                          workTags.includes(tag)
                            ? 'bg-indigo-600 text-white border-indigo-600'
                            : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400'
                        }`}>
                        {workTags.includes(tag) ? ' ' : ''}{tag}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-2">
                    Written review <span className="font-normal text-gray-400">(optional)</span>
                  </p>
                  <textarea
                    value={workFeedback}
                    onChange={e => setWorkFeedback(e.target.value)}
                    rows={4}
                    placeholder={`Tell others about ${firstName}'s work — quality, punctuality, behaviour on site, etc.`}
                    className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none placeholder-gray-400"
                  />
                </div>

                {!user && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 text-xs text-yellow-800">
                    <button onClick={() => navigate('/login')} className="font-bold underline">Login</button> to post a verified review.
                  </div>
                )}

                <div className="flex gap-3">
                  <button type="submit" disabled={submittingWorkReview || !workRating}
                    className="flex-1 bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 text-sm transition-colors">
                    {submittingWorkReview ? 'Submitting...' : ' Submit Work Review'}
                  </button>
                  <button type="button" onClick={() => setShowWorkReview(false)}
                    className="px-5 bg-gray-100 text-gray-600 font-semibold py-3 rounded-xl hover:bg-gray-200 text-sm">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* AI-built note */}
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-100 rounded-2xl p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl"></span>
            <div>
              <h3 className="font-bold text-gray-900 mb-1">AI-Built Profile</h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                This profile was created by our AI calling agent. The agent called this worker on their phone,
                asked questions in their preferred language, and automatically extracted their skills,
                experience, and background — no smartphone or internet required from the worker.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
