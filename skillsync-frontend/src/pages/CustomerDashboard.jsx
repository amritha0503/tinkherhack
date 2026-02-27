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
