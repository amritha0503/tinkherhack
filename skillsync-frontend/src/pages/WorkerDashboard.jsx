import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getWorker, getWorkerJobs, getTrustScore, completeJob, respondJob } from '../services/api'
import TrustBadge from '../components/TrustBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

export default function WorkerDashboard() {
  const { user } = useAuth()
  const [worker, setWorker] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getWorker(user.id), getWorkerJobs(user.id)])
      .then(([wRes, jRes]) => {
        setWorker(wRes.data)
        setJobs(jRes.data.jobs)
      })
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false))
  }, [user.id])

  const handleRespond = async (jobId, response) => {
    try {
      await respondJob(jobId, { response })
      setJobs(jobs.map(j => j.id === jobId ? { ...j, status: response === 'accepted' ? 'accepted' : 'cancelled' } : j))
      toast.success(`Job ${response}`)
    } catch { toast.error('Failed to update job') }
  }

  const handleComplete = async (jobId) => {
    try {
      const { data } = await completeJob(jobId)
      setJobs(jobs.map(j => j.id === jobId ? { ...j, status: 'completed' } : j))
      toast.success(`Job completed! QR ID: ${data.qr_id}`)
    } catch { toast.error('Failed to complete job') }
  }

  if (loading) return <LoadingSpinner text="Loading dashboard..." />

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
      {/* Profile Card */}
      {worker && (
        <div className="card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-orange-100 flex items-center justify-center text-2xl font-bold text-orange-600">
                {(worker.name || '?')[0].toUpperCase()}
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{worker.name || 'Complete your profile'}</h2>
                <p className="text-sm text-gray-500">{worker.skill_type || 'Skill not set'} · {worker.location_area || 'Location not set'}</p>
                <TrustBadge badge={worker.trust_badge} score={worker.trust_score} size="sm" />
              </div>
            </div>
            <Link to="/worker/profile" className="btn-secondary text-sm">Edit Profile</Link>
          </div>

          {!worker.profile_complete && (
            <div className="mt-3 bg-orange-50 border border-orange-200 rounded-lg p-3">
              <p className="text-sm text-orange-700">⚠️ Complete your profile to get more jobs</p>
            </div>
          )}

          {/* Stats */}
          <div className="mt-4 grid grid-cols-3 gap-3 text-center">
            {[
              { label: 'Trust Score', value: worker.trust_score },
              { label: 'Daily Rate', value: worker.daily_rate ? `₹${worker.daily_rate}` : 'N/A' },
              { label: 'Experience', value: worker.experience_years ? `${worker.experience_years} yrs` : 'N/A' },
            ].map(s => (
              <div key={s.label} className="bg-gray-50 rounded-lg p-2">
                <p className="text-lg font-bold text-gray-900">{s.value}</p>
                <p className="text-xs text-gray-500">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pending Jobs */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">📋 Job Requests ({jobs.length})</h3>
        {jobs.length === 0 ? (
          <div className="card text-center py-10 text-gray-400">
            <p className="text-4xl mb-2">📭</p>
            <p>No pending job requests</p>
          </div>
        ) : (
          <div className="space-y-3">
            {jobs.map(job => (
              <div key={job.id} className="card">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{job.ai_issue || job.description || 'Job Request'}</p>
                    <p className="text-xs text-gray-400 mt-0.5">Requested at {new Date(job.created_at).toLocaleString()}</p>
                    {job.ai_description && <p className="text-sm text-gray-600 mt-1">{job.ai_description}</p>}
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    job.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    job.status === 'accepted' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-600'
                  }`}>{job.status}</span>
                </div>
                {job.status === 'pending' && (
                  <div className="mt-3 flex gap-2">
                    <button onClick={() => handleRespond(job.id, 'accepted')} className="btn-primary text-sm flex-1">✅ Accept</button>
                    <button onClick={() => handleRespond(job.id, 'declined')} className="btn-secondary text-sm flex-1">❌ Decline</button>
                  </div>
                )}
                {job.status === 'accepted' && (
                  <button onClick={() => handleComplete(job.id)} className="mt-3 w-full bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors">
                    ✅ Mark as Completed
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
