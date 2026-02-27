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
