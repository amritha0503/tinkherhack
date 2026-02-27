import React from 'react'

export default function TrustBadge({ badge, score, size = 'md' }) {
  const cls = badge === 'Green' ? 'badge-green' : badge === 'Yellow' ? 'badge-yellow' : 'badge-red'
  const icon = badge === 'Green' ? '🟢' : badge === 'Yellow' ? '🟡' : '🔴'
  const small = size === 'sm'
  return (
    <div className="flex items-center gap-1.5">
      <span className={cls + (small ? ' text-xs' : '')}>
        {icon} {badge}
      </span>
      {score !== undefined && (
        <span className={`font-bold ${small ? 'text-sm' : 'text-base'} text-gray-700`}>{score}/100</span>
      )}
    </div>
  )
}
