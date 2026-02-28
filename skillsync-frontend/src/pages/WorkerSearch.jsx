import React, { useState, useEffect, useMemo } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { searchWorkers } from '../services/api'

const SKILLS = ['Electrician','Plumber','Carpenter','Mason','Painter','Welder','Cook','Other']
const BADGE_COLOR = { Green:'bg-green-100 text-green-800', Yellow:'bg-yellow-100 text-yellow-800', Red:'bg-red-100 text-red-800' }

const SORT_OPTIONS = [
  { value: 'distance',   label: 'Nearest first' },
  { value: 'trust',      label: 'Top rated' },
  { value: 'price_asc',  label: 'Price: low to high' },
  { value: 'price_desc', label: 'Price: high to low' },
  { value: 'exp',        label: 'Most experienced' },
]

function FilterChip({ label, onRemove }) {
  return (
    <span className="inline-flex items-center gap-1 bg-indigo-100 text-indigo-700 text-xs font-semibold px-2.5 py-1 rounded-full">
      {label}
      <button onClick={onRemove} className="hover:text-red-500 ml-0.5 leading-none">×</button>
    </span>
  )
}

export default function WorkerSearch() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Remote data
  const [workers, setWorkers]     = useState([])
  const [loading, setLoading]     = useState(true)
  const [userCoords, setUserCoords] = useState(null)
  const [locStatus, setLocStatus] = useState('getting')

  // Filter state
  const [skill,         setSkill]         = useState(searchParams.get('skill') || '')
  const [location,      setLocation]      = useState(searchParams.get('location') || '')
  const [minPrice,      setMinPrice]      = useState('')
  const [maxPrice,      setMaxPrice]      = useState('')
  const [maxDist,       setMaxDist]       = useState('')        // km
  const [minExp,        setMinExp]        = useState('')        // years
  const [minTrust,      setMinTrust]      = useState(0)
  const [aadhaarOnly,   setAadhaarOnly]   = useState(false)
  const [sortBy,        setSortBy]        = useState('distance')
  const [showFilters,   setShowFilters]   = useState(false)

  // Geolocation â†’ fetch on mount
  useEffect(() => {
    if (!navigator.geolocation) {
      setLocStatus('denied'); setSortBy('trust'); fetchWorkers(null); return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        setUserCoords(coords); setLocStatus('ok'); fetchWorkers(coords)
      },
      () => { setLocStatus('denied'); setSortBy('trust'); fetchWorkers(null) },
      { timeout: 8000 }
    )
  }, [])

  async function fetchWorkers(coords) {
    setLoading(true)
    try {
      const params = {}
      if (skill)    params.skill_type = skill
      if (location) params.location   = location
      if (coords)   { params.lat = coords.lat; params.lng = coords.lng; params.radius_km = 99999 }
      const res = await searchWorkers(params)
      setWorkers(res.data.workers || res.data || [])
    } catch { setWorkers([]) }
    finally  { setLoading(false) }
  }

  function applySearch(e) {
    e?.preventDefault()
    const p = {}
    if (skill)    p.skill    = skill
    if (location) p.location = location
    setSearchParams(p)
    fetchWorkers(userCoords)
  }

  // Client-side filter + sort
  const filtered = useMemo(() => {
    let list = [...workers]
    if (skill)       list = list.filter(w => !skill || w.skill_type === skill)
    if (location)    list = list.filter(w => !location || (w.location_area && w.location_area.toLowerCase().includes(location.toLowerCase())))
    if (minPrice)    list = list.filter(w => (w.daily_rate || 0) >= Number(minPrice))
    if (maxPrice)    list = list.filter(w => (w.daily_rate || 999999) <= Number(maxPrice))
    if (maxDist)     list = list.filter(w => w.distance_km == null || w.distance_km <= Number(maxDist))
    if (minExp)      list = list.filter(w => (w.experience_years || 0) >= Number(minExp))
    if (minTrust)    list = list.filter(w => (w.trust_score || 0) >= minTrust)
    if (aadhaarOnly) list = list.filter(w => w.aadhaar_verified)

    list.sort((a, b) => {
      if (sortBy === 'distance')   return (a.distance_km ?? 9999) - (b.distance_km ?? 9999)
      if (sortBy === 'trust')      return (b.trust_score  || 0)   - (a.trust_score  || 0)
      if (sortBy === 'price_asc')  return (a.daily_rate   || 0)   - (b.daily_rate   || 0)
      if (sortBy === 'price_desc') return (b.daily_rate   || 0)   - (a.daily_rate   || 0)
      if (sortBy === 'exp')        return (b.experience_years || 0) - (a.experience_years || 0)
      return 0
    })
    return list
  }, [workers, skill, minPrice, maxPrice, maxDist, minExp, minTrust, aadhaarOnly, sortBy])

  // Active chip labels
  const chips = [
    skill       && { label: `Skill: ${skill}`,          clear: () => setSkill('') },
    location    && { label: `Area: ${location}`,         clear: () => setLocation('') },
    minPrice    && { label: `Min Rs.${minPrice}/day`,     clear: () => setMinPrice('') },
    maxPrice    && { label: `Max Rs.${maxPrice}/day`,     clear: () => setMaxPrice('') },
    maxDist     && { label: `Within ${maxDist} km`,      clear: () => setMaxDist('') },
    minExp      && { label: `${minExp}+ yrs exp`,        clear: () => setMinExp('') },
    minTrust>0  && { label: `Trust >= ${minTrust}`,      clear: () => setMinTrust(0) },
    aadhaarOnly && { label: `Aadhaar verified`,          clear: () => setAadhaarOnly(false) },
  ].filter(Boolean)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
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

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* â”€â”€ Top search bar â”€â”€ */}
        <form onSubmit={applySearch} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-4 flex flex-wrap gap-3 items-end">
          {/* Skill */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Skill</label>
            <select value={skill} onChange={e => setSkill(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white min-w-[140px]">
              <option value="">All Skills</option>
              {SKILLS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          {/* Location */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Area / City</label>
            <input type="text" value={location} onChange={e => setLocation(e.target.value)}
              placeholder="e.g. Kozhikode"
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-w-[160px]" />
          </div>
          {/* Sort */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Sort by</label>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white min-w-[180px]">
              {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
          <div className="flex gap-2 ml-auto">
            <button type="button" onClick={() => setShowFilters(f => !f)}
              className={`flex items-center gap-1.5 border px-4 py-2 rounded-lg text-sm font-semibold transition-colors
                ${showFilters ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-indigo-400'}`}>
              Filters {chips.length > 0 && <span className="bg-indigo-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">{chips.length}</span>}
            </button>
            <button type="submit" className="bg-indigo-600 text-white font-bold px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm">
              Search
            </button>
          </div>
        </form>

        {/* â”€â”€ Expanded filter panel â”€â”€ */}
        {showFilters && (
          <div className="bg-white rounded-2xl border border-indigo-100 shadow-sm p-5 mb-4 grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {/* Price range */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Daily Rate (Rs.)</label>
              <div className="flex items-center gap-2">
                <input type="number" placeholder="Min" value={minPrice} onChange={e => setMinPrice(e.target.value)}
                  className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                <span className="text-gray-400 text-xs">to</span>
                <input type="number" placeholder="Max" value={maxPrice} onChange={e => setMaxPrice(e.target.value)}
                  className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              </div>
            </div>

            {/* Max distance */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                Max Distance{maxDist ? `: ${maxDist} km` : ''}
              </label>
              {locStatus !== 'ok' && <p className="text-xs text-amber-500 mb-1">Enable location for distance filter</p>}
              <input type="range" min={1} max={100} step={1} value={maxDist || 100}
                onChange={e => setMaxDist(e.target.value === '100' ? '' : e.target.value)}
                disabled={locStatus !== 'ok'}
                className="w-full accent-indigo-600 disabled:opacity-40" />
              <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>1 km</span><span>{maxDist ? `${maxDist} km` : 'Any'}</span><span>100 km</span></div>
            </div>

            {/* Min experience */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                Min Experience{minExp ? `: ${minExp} yrs` : ''}
              </label>
              <input type="range" min={0} max={20} step={1} value={minExp || 0}
                onChange={e => setMinExp(e.target.value === '0' ? '' : e.target.value)}
                className="w-full accent-indigo-600" />
              <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>Any</span><span>20 yrs</span></div>
            </div>

            {/* Min trust */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                Min Trust Score{minTrust > 0 ? `: ${minTrust}` : ''}
              </label>
              <input type="range" min={0} max={100} step={5} value={minTrust}
                onChange={e => setMinTrust(Number(e.target.value))}
                className="w-full accent-indigo-600" />
              <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                <span>Any</span>
                <span className="font-semibold text-indigo-500">{minTrust > 0 ? minTrust : 'Any'}</span>
                <span>100</span>
              </div>
            </div>

            {/* Trust badge quick-select */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Trust Badge</label>
              <div className="flex gap-2 flex-wrap">
                {[['Any',0],['Green',70],['Yellow',50],['Red',0]].map(([lbl, val]) => (
                  <button key={lbl} type="button"
                    onClick={() => setMinTrust(val)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-colors font-semibold
                      ${minTrust === val ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-200 text-gray-600 hover:border-indigo-400'}`}>
                    {lbl}
                  </button>
                ))}
              </div>
            </div>

            {/* Aadhaar toggle */}
            <div className="flex flex-col justify-center">
              <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Verification</label>
              <button type="button" onClick={() => setAadhaarOnly(v => !v)}
                className={`flex items-center gap-2 w-fit px-4 py-2 rounded-xl border text-sm font-semibold transition-colors
                  ${aadhaarOnly ? 'bg-green-50 border-green-400 text-green-700' : 'border-gray-200 text-gray-500 hover:border-green-400'}`}>
                <span className={`w-4 h-4 rounded border-2 flex items-center justify-center text-xs
                  ${aadhaarOnly ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300'}`}>
                  {aadhaarOnly ? '✓' : ''}
                </span>
                Aadhaar Verified Only
              </button>
            </div>

            {/* Reset */}
            <div className="flex items-end">
              <button type="button"
                onClick={() => { setMinPrice(''); setMaxPrice(''); setMaxDist(''); setMinExp(''); setMinTrust(0); setAadhaarOnly(false) }}
                className="text-sm text-red-400 hover:text-red-600 underline font-semibold">
                Reset all filters
              </button>
            </div>
          </div>
        )}

        {/* â”€â”€ Active filter chips â”€â”€ */}
        {chips.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="text-xs text-gray-400 self-center font-semibold">Active:</span>
            {chips.map((c, i) => <FilterChip key={i} label={c.label} onRemove={c.clear} />)}
          </div>
        )}

        {/* â”€â”€ Results header â”€â”€ */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-black text-gray-900">
            {loading ? 'Searching...' : `${filtered.length} Worker${filtered.length !== 1 ? 's' : ''} Found`}
          </h1>
          <div className="text-sm">
            {locStatus === 'getting' && <span className="text-gray-400">Getting your location...</span>}
            {locStatus === 'ok'      && <span className="text-green-600 font-semibold">Location active</span>}
            {locStatus === 'denied'  && <span className="text-gray-400">Location not available</span>}
          </div>
        </div>

        {/* â”€â”€ Worker cards â”€â”€ */}
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
            <p className="text-gray-400">Try adjusting your filters</p>
            {chips.length > 0 && (
              <button onClick={() => { setMinPrice(''); setMaxPrice(''); setMaxDist(''); setMinExp(''); setMinTrust(0); setAadhaarOnly(false) }}
                className="mt-4 text-sm text-indigo-600 underline font-semibold">Clear all filters</button>
            )}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map(w => (
              <div key={w.id}
                onClick={() => navigate(`/worker/${w.id}`)}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg transition-all cursor-pointer group p-6">
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
                  <div className="flex flex-col items-end gap-1">
                    {w.trust_badge && (
                      <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${BADGE_COLOR[w.trust_badge] || 'bg-gray-100 text-gray-600'}`}>
                        {w.trust_badge} {w.trust_score}
                      </span>
                    )}
                    {w.distance_km != null && (
                      <span className="text-xs font-semibold text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-full">
                        {w.distance_km < 1 ? `${Math.round(w.distance_km * 1000)} m away` : `${w.distance_km} km away`}
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
                    <span className="bg-green-50 text-green-700 text-xs px-2.5 py-1 rounded-full">Aadhaar Verified</span>
                  )}
                </div>

                {w.bio_text && (
                  <p className="text-xs text-gray-400 line-clamp-2 mb-4 leading-relaxed">{w.bio_text}</p>
                )}

                <div className="flex items-center justify-between pt-3 border-t border-gray-50">
                  <span className="text-sm font-bold text-gray-900">
                    Rs.{w.daily_rate || '--'}<span className="text-xs font-normal text-gray-400">/day</span>
                  </span>
                  <span className="text-xs text-indigo-600 font-semibold group-hover:underline">View Profile &rarr;</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

