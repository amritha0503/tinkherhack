import React from 'react'
import { useNavigate } from 'react-router-dom'
import TrustBadge from './TrustBadge'

export default function WorkerCard({ worker, onHire }) {
  const navigate = useNavigate()
  return (
    <div className="card hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate(`/worker/${worker.id}`)}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-xl font-bold text-orange-600">
            {(worker.name || '?')[0].toUpperCase()}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{worker.name || 'Unnamed Worker'}</h3>
            <p className="text-sm text-gray-500">{worker.skill_type} · {worker.experience_years || 0} yrs exp</p>
          </div>
        </div>
        <TrustBadge badge={worker.trust_badge} score={worker.trust_score} size="sm" />
      </div>

      <div className="mt-3 flex flex-wrap gap-3 text-sm text-gray-600">
        <span>📍 {worker.location_area || 'Location N/A'}</span>
        <span>📏 {worker.distance_km} km away</span>
        <span>💰 ₹{worker.daily_rate || '?'}/day</span>
        {worker.avg_rating > 0 && <span>⭐ {worker.avg_rating} ({worker.verified_jobs} jobs)</span>}
      </div>

      {onHire && (
        <button
          onClick={e => { e.stopPropagation(); onHire(worker) }}
          className="mt-3 w-full btn-primary text-sm"
        >
          Hire Now
        </button>
      )}
    </div>
  )
}
