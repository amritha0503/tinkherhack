import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span className="font-bold text-lg text-gray-900">SkillSync</span>
        </Link>

        <div className="flex items-center gap-3">
          {user?.role === 'worker' && (
            <>
              <Link to="/worker/dashboard" className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
              <Link to="/worker/profile" className="text-sm text-gray-600 hover:text-gray-900">Profile</Link>
            </>
          )}
          {user?.role === 'customer' && (
            <>
              <Link to="/customer/dashboard" className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
              <Link to="/customer/search" className="text-sm text-gray-600 hover:text-gray-900">Find Workers</Link>
            </>
          )}
          <div className="flex items-center gap-2 ml-3 pl-3 border-l border-gray-200">
            <span className="text-xs text-gray-500 capitalize">{user?.role}</span>
            <button onClick={handleLogout} className="text-sm text-red-500 hover:text-red-700 font-medium">Logout</button>
          </div>
        </div>
      </div>
    </nav>
  )
}
