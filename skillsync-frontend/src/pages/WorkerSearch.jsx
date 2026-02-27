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
                  <p className="text-xs text-gray-400 line-clamp-2 mb-4 leading-relaxed">{w.bio_text}</p>
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
