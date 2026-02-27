import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import CustomerDashboard from './pages/CustomerDashboard'
import WorkerSearch from './pages/WorkerSearch'
import WorkerDetail from './pages/WorkerDetail'
import JobDetail from './pages/JobDetail'
import AICallPage from './pages/AICallPage'

function ProtectedRoute({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/"           element={<Landing />} />
        <Route path="/login"      element={<Login />} />
        <Route path="/search"     element={<WorkerSearch />} />
        <Route path="/ai-call"    element={<AICallPage />} />
        <Route path="/worker/:workerId" element={<WorkerDetail />} />
        <Route path="/dashboard"  element={<ProtectedRoute><CustomerDashboard /></ProtectedRoute>} />
        <Route path="/job/:jobId" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
        <Route path="*"           element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
