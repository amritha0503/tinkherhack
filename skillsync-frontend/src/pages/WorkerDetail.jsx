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
                  "{worker.bio_text}"
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
