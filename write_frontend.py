"""Writes all SkillSync frontend source files."""
import os

BASE = r"C:\Users\Amritha\Desktop\tinkherhack\skillsync-frontend\src"

files = {}

# ─────────────────────────────────────────────────────────────────────────────
files["pages/Landing.jsx"] = r"""
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const SKILLS = ['All Skills','Electrician','Plumber','Carpenter','Mason','Painter','Welder','Other']

const FEATURES = [
  { icon:'📞', title:'AI Calls the Worker', desc:"Our AI agent calls workers directly on their phone — no smartphone or internet needed from their side." },
  { icon:'🌐', title:'Any Language', desc:'Workers answer in Hindi, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam or English. AI understands all.' },
  { icon:'🤖', title:'Auto-Built Portfolio', desc:'AI listens to their voice answers and automatically extracts skills, experience, rate and bio.' },
  { icon:'⭐', title:'Trust Score', desc:'Every worker gets a verified Trust Badge — Green, Yellow or Red — based on job history and Aadhaar verification.' },
  { icon:'📸', title:'Work Photos', desc:"Customers upload photos of problems. AI identifies the issue and recommends the right worker type." },
  { icon:'🛡️', title:'Emergency SOS', desc:"Workers in distress can trigger an SOS alert. Real-time safety net for India's invisible workforce." },
]

export default function Landing() {
  const navigate = useNavigate()
  const [skill, setSkill] = useState('All Skills')
  const [location, setLocation] = useState('')

  function handleSearch(e) {
    e.preventDefault()
    const params = new URLSearchParams()
    if (skill !== 'All Skills') params.set('skill', skill)
    if (location.trim()) params.set('location', location.trim())
    navigate(`/search?${params.toString()}`)
  }

  return (
    <div className="min-h-screen bg-white">

      {/* NAV */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-gray-100 sticky top-0 bg-white z-50 shadow-sm">
        <div className="flex items-center gap-1">
          <span className="text-2xl font-black text-indigo-600">Skill</span>
          <span className="text-2xl font-black text-gray-800">Sync</span>
        </div>
        <div className="flex gap-3 items-center">
          <button onClick={() => navigate('/ai-call')}
            className="text-sm text-gray-600 hover:text-indigo-600 font-medium px-3 py-1.5">
            For Workers
          </button>
          <button onClick={() => navigate('/search')}
            className="text-sm text-gray-600 hover:text-indigo-600 font-medium px-3 py-1.5">
            Browse Workers
          </button>
          <button onClick={() => navigate('/login')}
            className="text-sm bg-indigo-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
            Login
          </button>
        </div>
      </nav>

      {/* HERO */}
      <section className="bg-gradient-to-br from-indigo-50 via-white to-orange-50 py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full mb-6 uppercase tracking-wide">
            Digital Identity for India's Invisible Workforce
          </div>
          <h1 className="text-5xl md:text-6xl font-black text-gray-900 mb-6 leading-tight">
            Find Trusted Skilled<br />
            <span className="text-indigo-600">Workers Near You</span>
          </h1>
          <p className="text-xl text-gray-500 mb-10 max-w-2xl mx-auto">
            Browse AI-verified profiles of plumbers, electricians, carpenters and more.
            Profiles built by our AI agent calling workers in their own language.
          </p>

          <form onSubmit={handleSearch} className="bg-white rounded-2xl shadow-xl border border-gray-100 p-3 flex flex-col md:flex-row gap-3 max-w-2xl mx-auto">
            <select value={skill} onChange={e => setSkill(e.target.value)}
              className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
              {SKILLS.map(s => <option key={s}>{s}</option>)}
            </select>
            <input type="text" value={location} onChange={e => setLocation(e.target.value)}
              placeholder="City or area (e.g. Kozhikode)"
              className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            <button type="submit"
              className="bg-indigo-600 text-white font-bold px-8 py-3 rounded-xl hover:bg-indigo-700 transition-colors whitespace-nowrap">
              Find Workers →
            </button>
          </form>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-black text-center text-gray-900 mb-3">How Worker Profiles Are Built</h2>
          <p className="text-center text-gray-400 mb-14 max-w-xl mx-auto">
            Most workers don't have smartphones. Our AI calls them on any phone.
          </p>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { n:'1', icon:'📱', title:'AI Places Call', desc:"AI calls the worker's mobile — works on any phone, no internet." },
              { n:'2', icon:'🌐', title:'Pick Language', desc:'Worker presses 1–8 on keypad to choose their language.' },
              { n:'3', icon:'🎙️', title:'Answer Questions', desc:'AI asks about skills, experience and rate. Worker speaks naturally.' },
              { n:'4', icon:'✅', title:'Profile Ready', desc:'AI extracts a verified portfolio. Customers can now find and hire.' },
            ].map(item => (
              <div key={item.n} className="text-center">
                <div className="w-10 h-10 bg-indigo-600 text-white rounded-full flex items-center justify-center font-black text-base mx-auto mb-3">{item.n}</div>
                <div className="text-3xl mb-2">{item.icon}</div>
                <h3 className="font-bold text-gray-900 mb-1 text-sm">{item.title}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-12 text-center">
            <button onClick={() => navigate('/ai-call')}
              className="bg-orange-500 text-white font-bold px-8 py-3 rounded-xl hover:bg-orange-600 transition-colors">
              Try AI Call Demo →
            </button>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="py-20 px-6 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-black text-center text-gray-900 mb-12">Everything You Need</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {FEATURES.map(f => (
              <div key={f.title} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">{f.icon}</div>
                <h3 className="font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-indigo-600 text-white text-center">
        <h2 className="text-4xl font-black mb-4">Ready to find a worker?</h2>
        <p className="text-indigo-200 mb-8 max-w-lg mx-auto">Browse AI-verified profiles. Free to search, no signup needed.</p>
        <div className="flex gap-4 justify-center flex-wrap">
          <button onClick={() => navigate('/search')}
            className="bg-white text-indigo-600 font-bold px-8 py-3 rounded-xl hover:bg-indigo-50 transition-colors">
            Browse Workers
          </button>
          <button onClick={() => navigate('/login')}
            className="border-2 border-white text-white font-bold px-8 py-3 rounded-xl hover:bg-indigo-700 transition-colors">
            Login / Sign Up
          </button>
        </div>
      </section>

      <footer className="py-8 px-6 bg-gray-900 text-gray-400 text-center text-sm">
        <div className="font-black text-white text-lg mb-1">SkillSync</div>
        <div>Digital Identity for India's Invisible Workforce</div>
      </footer>
    </div>
  )
}
""".lstrip()

# ─────────────────────────────────────────────────────────────────────────────
files["pages/WorkerSearch.jsx"] = r"""
import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { searchWorkers } from '../services/api'

const SKILLS = ['','Electrician','Plumber','Carpenter','Mason','Painter','Welder','Other']
const BADGE_COLOR = { Green:'bg-green-100 text-green-800', Yellow:'bg-yellow-100 text-yellow-800', Red:'bg-red-100 text-red-800' }

export default function WorkerSearch() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  const [workers, setWorkers] = useState([])
  const [loading, setLoading] = useState(true)
  const [skill, setSkill] = useState(searchParams.get('skill') || '')
  const [location, setLocation] = useState(searchParams.get('location') || '')
  const [minTrust, setMinTrust] = useState(0)

  useEffect(() => { fetchWorkers() }, [])

  async function fetchWorkers() {
    setLoading(true)
    try {
      const params = {}
      if (skill) params.skill_type = skill
      if (location) params.location = location
      const res = await searchWorkers(params)
      setWorkers(res.data.workers || res.data || [])
    } catch {
      setWorkers([])
    } finally {
      setLoading(false)
    }
  }

  function applyFilter(e) {
    e.preventDefault()
    const p = {}
    if (skill) p.skill = skill
    if (location) p.location = location
    setSearchParams(p)
    fetchWorkers()
  }

  const filtered = workers.filter(w => w.trust_score >= minTrust)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top nav */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100 sticky top-0 z-40 shadow-sm">
        <button onClick={() => navigate('/')} className="flex items-center gap-1">
          <span className="text-xl font-black text-indigo-600">Skill</span>
          <span className="text-xl font-black text-gray-800">Sync</span>
        </button>
        <div className="flex gap-3">
          <button onClick={() => navigate('/ai-call')} className="text-sm text-gray-500 hover:text-indigo-600 px-3 py-1.5">For Workers</button>
          <button onClick={() => navigate('/login')} className="text-sm bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-semibold">Login</button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Filter bar */}
        <form onSubmit={applyFilter} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-8 flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Skill</label>
            <select value={skill} onChange={e => setSkill(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white min-w-[140px]">
              <option value="">All Skills</option>
              {SKILLS.filter(Boolean).map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Location</label>
            <input type="text" value={location} onChange={e => setLocation(e.target.value)}
              placeholder="City or area"
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[160px]" />
          </div>
          <div className="flex-1 min-w-[160px]">
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">
              Min Trust Score: {minTrust}
            </label>
            <input type="range" min={0} max={100} step={5} value={minTrust}
              onChange={e => setMinTrust(Number(e.target.value))}
              className="w-full accent-indigo-600" />
          </div>
          <button type="submit"
            className="bg-indigo-600 text-white font-bold px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm">
            Search
          </button>
        </form>

        {/* Results */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-black text-gray-900">
            {loading ? 'Searching...' : `${filtered.length} Worker${filtered.length !== 1 ? 's' : ''} Found`}
          </h1>
        </div>

        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_,i) => (
              <div key={i} className="bg-white rounded-2xl p-6 animate-pulse border border-gray-100">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 bg-gray-200 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded" />
                  <div className="h-3 bg-gray-200 rounded w-5/6" />
                </div>
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">🔍</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">No workers found</h3>
            <p className="text-gray-400">Try adjusting your filters or lowering the trust score minimum</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map(w => (
              <div key={w.id}
                onClick={() => navigate(`/worker/${w.id}`)}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg transition-shadow cursor-pointer group p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-14 h-14 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-black text-xl">
                      {(w.name || '?')[0].toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                        {w.name || 'Unknown'}
                      </h3>
                      <p className="text-sm text-gray-400">{w.location_area || 'Location TBD'}</p>
                    </div>
                  </div>
                  <div>
                    {w.trust_badge && (
                      <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${BADGE_COLOR[w.trust_badge] || 'bg-gray-100 text-gray-600'}`}>
                        {w.trust_badge} {w.trust_score}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-3">
                  <span className="bg-indigo-50 text-indigo-700 text-xs font-semibold px-2.5 py-1 rounded-full">
                    {w.skill_type || 'General'}
                  </span>
                  <span className="bg-gray-100 text-gray-600 text-xs px-2.5 py-1 rounded-full">
                    {w.experience_years || 0} yrs exp
                  </span>
                  {w.aadhaar_verified && (
                    <span className="bg-green-50 text-green-700 text-xs px-2.5 py-1 rounded-full">✓ Aadhaar</span>
                  )}
                </div>

                {w.bio && (
                  <p className="text-xs text-gray-400 line-clamp-2 mb-4 leading-relaxed">{w.bio}</p>
                )}

                <div className="flex items-center justify-between pt-3 border-t border-gray-50">
                  <span className="text-sm font-bold text-gray-900">
                    ₹{w.daily_rate || '—'}<span className="text-xs font-normal text-gray-400">/day</span>
                  </span>
                  <span className="text-xs text-indigo-600 font-semibold group-hover:underline">View Profile →</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
""".lstrip()

# ─────────────────────────────────────────────────────────────────────────────
files["pages/WorkerDetail.jsx"] = r"""
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getWorker, createJob } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

const BADGE_COLOR = { Green:'bg-green-100 text-green-800', Yellow:'bg-yellow-100 text-yellow-800', Red:'bg-red-100 text-red-800' }

export default function WorkerDetail() {
  const { workerId } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [worker, setWorker] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showHireForm, setShowHireForm] = useState(false)
  const [jobDesc, setJobDesc] = useState('')
  const [hiring, setHiring] = useState(false)

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

  async function handleHire(e) {
    e.preventDefault()
    if (!user) { navigate('/login'); return }
    setHiring(true)
    try {
      await createJob({ worker_id: workerId, description: jobDesc, customer_id: user.id })
      toast.success('Job request sent! Worker will be notified.')
      setShowHireForm(false)
      setJobDesc('')
    } catch {
      toast.error('Failed to send job request')
    } finally {
      setHiring(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Loading profile...</p>
      </div>
    </div>
  )

  if (!worker) return null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back nav */}
      <nav className="flex items-center px-6 py-4 bg-white border-b border-gray-100 sticky top-0 z-40">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-900 mr-4">
          ← Back
        </button>
        <span className="font-black text-indigo-600 text-lg">Skill</span><span className="font-black text-gray-800 text-lg">Sync</span>
      </nav>

      <div className="max-w-3xl mx-auto px-4 py-8">

        {/* Profile header */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 mb-6">
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            <div className="w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-black text-4xl shrink-0">
              {(worker.name || '?')[0].toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-3 mb-2">
                <h1 className="text-2xl font-black text-gray-900">{worker.name || 'Worker'}</h1>
                {worker.trust_badge && (
                  <span className={`text-sm font-bold px-3 py-1 rounded-full ${BADGE_COLOR[worker.trust_badge] || 'bg-gray-100'}`}>
                    {worker.trust_badge} • Score {worker.trust_score}
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
                    ✓ Aadhaar Verified
                  </span>
                )}
              </div>

              {worker.bio && (
                <p className="text-gray-600 leading-relaxed text-sm mb-4 bg-gray-50 rounded-xl p-4 italic">
                  "{worker.bio}"
                </p>
              )}

              <div className="flex items-center justify-between">
                <div className="text-2xl font-black text-gray-900">
                  ₹{worker.daily_rate || '—'}<span className="text-sm font-normal text-gray-400"> per day</span>
                </div>
                <button onClick={() => setShowHireForm(!showHireForm)}
                  className="bg-indigo-600 text-white font-bold px-8 py-3 rounded-xl hover:bg-indigo-700 transition-colors">
                  {showHireForm ? 'Cancel' : 'Hire This Worker'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Hire form */}
        {showHireForm && (
          <div className="bg-white rounded-2xl border border-indigo-200 shadow-sm p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Describe your work</h2>
            {!user && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-4 text-sm text-yellow-800">
                You need to <button onClick={() => navigate('/login')} className="font-bold underline">login</button> first to hire a worker.
              </div>
            )}
            <form onSubmit={handleHire} className="space-y-4">
              <textarea
                rows={4}
                value={jobDesc}
                onChange={e => setJobDesc(e.target.value)}
                placeholder="Describe what work you need done. E.g. 'Fix leaking pipe under kitchen sink', 'Paint 3 bedroom walls', etc."
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                required
              />
              <button type="submit" disabled={hiring || !user}
                className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                {hiring ? 'Sending...' : 'Send Job Request'}
              </button>
            </form>
          </div>
        )}

        {/* Profile source note */}
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-100 rounded-2xl p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🤖</span>
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
""".lstrip()

# ─────────────────────────────────────────────────────────────────────────────
files["pages/Login.jsx"] = r"""
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { sendOTP, verifyOTP, registerCustomer } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [step, setStep] = useState('phone')   // phone | otp | name
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [token, setToken] = useState('')

  async function handleSendOTP(e) {
    e.preventDefault()
    if (phone.length < 10) { toast.error('Enter a valid 10-digit phone number'); return }
    setLoading(true)
    try {
      await sendOTP(phone)
      toast.success('OTP sent! Check server logs for demo OTP.')
      setStep('otp')
    } catch {
      toast.error('Failed to send OTP')
    } finally { setLoading(false) }
  }

  async function handleVerifyOTP(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await verifyOTP(phone, otp)
      if (res.data.token) {
        // Existing worker
        login({ id: res.data.user_id, phone, role: 'customer' }, res.data.token)
        toast.success('Welcome back!')
        navigate('/dashboard')
      } else if (res.data.success) {
        setToken(res.data.temp_token || '')
        setStep('name')
      }
    } catch {
      toast.error('Incorrect OTP')
    } finally { setLoading(false) }
  }

  async function handleRegister(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await registerCustomer({ name, phone })
      const t = res.data.token || token
      login({ id: res.data.id || res.data.customer_id, phone, role: 'customer', name }, t)
      toast.success(`Welcome, ${name}!`)
      navigate('/dashboard')
    } catch {
      toast.error('Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex flex-col">
      <nav className="flex items-center px-6 py-4">
        <button onClick={() => navigate('/')} className="flex items-center gap-1">
          <span className="text-xl font-black text-indigo-600">Skill</span>
          <span className="text-xl font-black text-gray-800">Sync</span>
        </button>
      </nav>

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">

            {step === 'phone' && (
              <>
                <h1 className="text-2xl font-black text-gray-900 mb-2">Customer Login</h1>
                <p className="text-gray-400 text-sm mb-8">Find and hire verified skilled workers near you</p>
                <form onSubmit={handleSendOTP} className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Mobile Number</label>
                    <div className="flex">
                      <span className="bg-gray-100 border border-gray-200 border-r-0 rounded-l-xl px-3 py-3 text-sm text-gray-500 font-semibold">+91</span>
                      <input type="tel" value={phone} onChange={e => setPhone(e.target.value.replace(/\D/,'').slice(0,10))}
                        placeholder="9876543210" maxLength={10}
                        className="flex-1 border border-gray-200 rounded-r-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                    </div>
                  </div>
                  <button type="submit" disabled={loading}
                    className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                    {loading ? 'Sending...' : 'Send OTP'}
                  </button>
                </form>
                <div className="mt-6 pt-6 border-t border-gray-100 text-center">
                  <p className="text-xs text-gray-400 mb-3">Are you a worker? No need to login.</p>
                  <button onClick={() => navigate('/ai-call')}
                    className="text-orange-500 font-semibold text-sm hover:underline">
                    Register as Worker via AI Call →
                  </button>
                </div>
              </>
            )}

            {step === 'otp' && (
              <>
                <button onClick={() => setStep('phone')} className="text-sm text-gray-400 hover:text-gray-600 mb-6">← Back</button>
                <h1 className="text-2xl font-black text-gray-900 mb-2">Enter OTP</h1>
                <p className="text-gray-400 text-sm mb-8">OTP sent to +91 {phone}</p>
                <form onSubmit={handleVerifyOTP} className="space-y-4">
                  <input type="text" value={otp} onChange={e => setOtp(e.target.value.replace(/\D/,'').slice(0,6))}
                    placeholder="6-digit OTP" maxLength={6}
                    className="w-full border border-gray-200 rounded-xl px-4 py-3 text-center text-2xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  <p className="text-xs text-center text-gray-400">For demo: check the backend server terminal for OTP</p>
                  <button type="submit" disabled={loading || otp.length < 6}
                    className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                    {loading ? 'Verifying...' : 'Verify OTP'}
                  </button>
                </form>
              </>
            )}

            {step === 'name' && (
              <>
                <h1 className="text-2xl font-black text-gray-900 mb-2">Welcome!</h1>
                <p className="text-gray-400 text-sm mb-8">Just tell us your name to get started</p>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Your Name</label>
                    <input type="text" value={name} onChange={e => setName(e.target.value)}
                      placeholder="Full name"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <button type="submit" disabled={loading}
                    className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                    {loading ? 'Creating account...' : 'Create Account →'}
                  </button>
                </form>
              </>
            )}

          </div>
        </div>
      </div>
    </div>
  )
}
""".lstrip()

# ─────────────────────────────────────────────────────────────────────────────
files["pages/CustomerDashboard.jsx"] = r"""
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getWorkerJobs } from '../services/api'
import toast from 'react-hot-toast'

const STATUS_STYLE = {
  pending:   'bg-yellow-100 text-yellow-800',
  accepted:  'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  disputed:  'bg-red-100 text-red-800',
}

export default function CustomerDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    async function load() {
      try {
        const res = await getWorkerJobs(user.id)
        setJobs(res.data.jobs || res.data || [])
      } catch {
        setJobs([])
      } finally { setLoading(false) }
    }
    load()
  }, [user])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100 sticky top-0 z-40 shadow-sm">
        <button onClick={() => navigate('/')} className="flex items-center gap-1">
          <span className="text-xl font-black text-indigo-600">Skill</span>
          <span className="text-xl font-black text-gray-800">Sync</span>
        </button>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">Hi, {user?.name || user?.phone}</span>
          <button onClick={() => { logout(); navigate('/') }}
            className="text-sm text-gray-400 hover:text-red-500">Logout</button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-black text-gray-900">My Dashboard</h1>
            <p className="text-gray-400 text-sm">Manage your job requests and hires</p>
          </div>
          <button onClick={() => navigate('/search')}
            className="bg-indigo-600 text-white font-bold px-6 py-3 rounded-xl hover:bg-indigo-700 transition-colors">
            Find Workers +
          </button>
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { icon:'🔍', label:'Find Workers',  action:() => navigate('/search') },
            { icon:'📋', label:'Browse Jobs',   action:() => navigate('/search') },
            { icon:'📞', label:'AI Call Demo',  action:() => navigate('/ai-call') },
            { icon:'🏠', label:'Home',          action:() => navigate('/') },
          ].map(item => (
            <button key={item.label} onClick={item.action}
              className="bg-white border border-gray-100 rounded-2xl p-4 text-center hover:shadow-md hover:border-indigo-200 transition-all">
              <div className="text-2xl mb-2">{item.icon}</div>
              <div className="text-xs font-semibold text-gray-600">{item.label}</div>
            </button>
          ))}
        </div>

        {/* Jobs */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-bold text-gray-900">My Job Requests</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-gray-400">Loading jobs...</div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-4xl mb-3">📋</div>
              <h3 className="font-bold text-gray-700 mb-2">No jobs yet</h3>
              <p className="text-gray-400 text-sm mb-6">Find a worker and send your first job request</p>
              <button onClick={() => navigate('/search')}
                className="bg-indigo-600 text-white font-bold px-6 py-3 rounded-xl hover:bg-indigo-700">
                Browse Workers
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-50">
              {jobs.map(job => (
                <div key={job.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 mb-1">{job.description || 'Job Request'}</p>
                    <p className="text-xs text-gray-400">{new Date(job.created_at).toLocaleDateString('en-IN')}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${STATUS_STYLE[job.status] || 'bg-gray-100 text-gray-600'}`}>
                      {job.status}
                    </span>
                    <button onClick={() => navigate(`/job/${job.id}`)}
                      className="text-xs text-indigo-600 hover:underline">View</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
""".lstrip()

# ─────────────────────────────────────────────────────────────────────────────
files["App.jsx"] = r"""
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import CustomerDashboard from './pages/CustomerDashboard'
import WorkerSearch from './pages/WorkerSearch'
import WorkerDetail from './pages/WorkerDetail'
import JobDetail from './pages/JobDetail'
import AICallPage from './pages/AICallPage'

function ProtectedRoute({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/"           element={<Landing />} />
        <Route path="/login"      element={<Login />} />
        <Route path="/search"     element={<WorkerSearch />} />
        <Route path="/ai-call"    element={<AICallPage />} />
        <Route path="/worker/:workerId" element={<WorkerDetail />} />
        <Route path="/dashboard"  element={<ProtectedRoute><CustomerDashboard /></ProtectedRoute>} />
        <Route path="/job/:jobId" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
        <Route path="*"           element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
""".lstrip()

# ─────────────────────────────────────────────────────────────────────────────
files["services/api.js"] = r"""
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ─── Auth ───────────────────────────────────────────────────────────────────
export const sendOTP        = (phone)       => api.post('/auth/send-otp', { phone })
export const verifyOTP      = (phone, otp)  => api.post('/auth/verify-otp', { phone, otp })

// ─── Workers ────────────────────────────────────────────────────────────────
export const searchWorkers  = (params)      => api.get('/workers/search', { params })
export const getWorker      = (id)          => api.get(`/workers/${id}`)
export const updateWorker   = (id, data)    => api.put(`/workers/${id}`, data)
export const getTrustScore  = (id)          => api.get(`/workers/${id}/trust-score`)
export const getWorkerLedger= (id)          => api.get(`/workers/${id}/ledger`)
export const uploadPhotos   = (id, form)    => api.post(`/workers/${id}/photos`, form, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const uploadVoiceBio = (id, form)    => api.post(`/workers/${id}/voice-bio`, form, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const aadhaarVerify  = (id, data)    => api.post(`/workers/${id}/aadhaar`, data)

// ─── Customers ──────────────────────────────────────────────────────────────
export const registerCustomer = (data)      => api.post('/customers/register', data)
export const getCustomer      = (id)        => api.get(`/customers/${id}`)

// ─── Jobs ───────────────────────────────────────────────────────────────────
export const createJob      = (data)        => api.post('/jobs/create', data)
export const getJob         = (id)          => api.get(`/jobs/${id}`)
export const getWorkerJobs  = (id)          => api.get(`/jobs/worker/${id}`)
export const respondJob     = (id, action)  => api.post(`/jobs/${id}/respond`, { action })
export const completeJob    = (id, data)    => api.post(`/jobs/${id}/complete`, data)
export const disputeJob     = (id, reason)  => api.post(`/jobs/${id}/dispute`, { reason })

// ─── Reviews ────────────────────────────────────────────────────────────────
export const submitReview   = (data)        => api.post('/reviews/submit', data)

// ─── Calls ──────────────────────────────────────────────────────────────────
export const initiateCall   = (data)        => api.post('/calls/initiate', data)
export const endCall        = (callId)      => api.post(`/calls/${callId}/end`)

// ─── Emergency ──────────────────────────────────────────────────────────────
export const triggerEmergency = (data)      => api.post('/emergency/trigger', data)

// ─── AI Call Agent ──────────────────────────────────────────────────────────
export const getLanguages   = ()            => api.get('/ai-call/languages')
export const getQuestions   = (phone, lang) => api.post('/ai-call/questions', { phone, language_key: lang })
export const extractProfile = (data)        => api.post('/ai-call/extract-profile', data)
export const saveProfile    = (phone, profile) => api.post(`/ai-call/save-profile?phone=${phone}`, profile)
export const transcribeVoice= (form)        => api.post('/ai-call/voice-answer', form, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

export default api
""".lstrip()

# Write all files
for rel_path, content in files.items():
    full_path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written: {rel_path} ({len(content.splitlines())} lines)')

print('All files written successfully!')
