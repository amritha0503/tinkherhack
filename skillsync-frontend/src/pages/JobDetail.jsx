import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getJob, respondJob, completeJob, disputeJob, scanQR, submitReview } from '../services/api'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

export default function JobDetail() {
  const { jobId } = useParams()
  const { user } = useAuth()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [qrId, setQrId] = useState('')
  const [reviewForm, setReviewForm] = useState({ rating: 5, text: '' })
  const [showReview, setShowReview] = useState(false)

  const reload = () => getJob(jobId).then(r => setJob(r.data)).catch(() => toast.error('Failed to load job'))

  useEffect(() => {
    reload().finally(() => setLoading(false))
  }, [jobId])

  const statusColor = {
    pending: 'bg-yellow-100 text-yellow-800',
    accepted: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-gray-100 text-gray-600',
    disputed: 'bg-red-100 text-red-800',
  }

  const handleScanQR = async () => {
    if (!qrId.trim()) return toast.error('Enter QR ID')
    try {
      const { data } = await scanQR(qrId.trim())
      toast.success(`QR valid: ${data.worker_name} — ${data.job_type}`)
      setShowReview(true)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid QR')
    }
  }

  const handleSubmitReview = async e => {
    e.preventDefault()
    try {
      const { data } = await submitReview(qrId.trim(), reviewForm.rating, reviewForm.text)
      toast.success(`Review submitted! New trust score: ${data.new_trust_score}`)
      setShowReview(false)
      reload()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Review failed')
    }
  }

  const handleDispute = async () => {
    const reason = window.prompt('Please describe the dispute:')
    if (!reason) return
    try {
      await disputeJob(jobId, reason)
      toast.success('Dispute logged')
      reload()
    } catch { toast.error('Failed to dispute') }
  }

  if (loading) return <LoadingSpinner />
  if (!job) return <div className="text-center py-20 text-gray-400">Job not found</div>

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-xl font-bold text-gray-900">Job Request</h1>
          <span className={`text-sm px-3 py-1 rounded-full font-medium ${statusColor[job.job_status] || 'bg-gray-100 text-gray-600'}`}>
            {job.job_status}
          </span>
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          <p><span className="font-medium text-gray-900">ID:</span> {job.id}</p>
          <p><span className="font-medium text-gray-900">Description:</span> {job.complaint_description || 'N/A'}</p>
          {job.ai_issue_type && <p><span className="font-medium text-gray-900">AI Issue Type:</span> {job.ai_issue_type}</p>}
          {job.ai_description && (
            <div className="bg-blue-50 rounded-lg p-3 mt-2">
              <p className="text-xs font-medium text-blue-700 mb-1">🤖 AI Analysis</p>
              <p className="text-blue-800">{job.ai_description}</p>
            </div>
          )}
          <p><span className="font-medium text-gray-900">Created:</span> {new Date(job.created_at).toLocaleString()}</p>
          {job.completed_at && <p><span className="font-medium text-gray-900">Completed:</span> {new Date(job.completed_at).toLocaleString()}</p>}
        </div>

        {/* Actions */}
        <div className="mt-4 space-y-2">
          {job.job_status === 'completed' && user?.role === 'customer' && (
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <p className="text-sm font-medium text-gray-700">📱 Submit Review via QR</p>
              <div className="flex gap-2">
                <input className="input flex-1 text-sm" value={qrId} onChange={e => setQrId(e.target.value)} placeholder="Paste QR ID from worker" />
                <button onClick={handleScanQR} className="btn-primary whitespace-nowrap text-sm">Scan</button>
              </div>
            </div>
          )}

          {showReview && (
            <form onSubmit={handleSubmitReview} className="bg-orange-50 rounded-lg p-3 space-y-2">
              <p className="text-sm font-medium text-orange-800">⭐ Leave a Review</p>
              <div className="flex gap-2">
                {[1,2,3,4,5].map(s => (
                  <button key={s} type="button" onClick={() => setReviewForm({...reviewForm, rating: s})}
                    className={`text-xl ${s <= reviewForm.rating ? 'opacity-100' : 'opacity-30'}`}>⭐</button>
                ))}
              </div>
              <textarea className="input text-sm resize-none" rows={2} value={reviewForm.text}
                onChange={e => setReviewForm({...reviewForm, text: e.target.value})} placeholder="Write your review..." />
              <button type="submit" className="btn-primary w-full text-sm">Submit Review</button>
            </form>
          )}

          {(job.job_status === 'accepted' || job.job_status === 'pending') && user?.role === 'customer' && (
            <button onClick={handleDispute} className="w-full border border-red-300 text-red-600 hover:bg-red-50 font-medium px-4 py-2 rounded-lg text-sm transition-colors">
              ⚠️ Raise Dispute
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
