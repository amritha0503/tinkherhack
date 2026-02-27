import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { customerLogin, customerRegister } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [mode, setMode]         = useState('login')   // 'login' | 'register'
  const [name, setName]         = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm]   = useState('')
  const [loading, setLoading]   = useState(false)

  async function handleLogin(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await customerLogin({ email, password })
      login({ id: res.data.user_id, email, name: res.data.name, role: 'customer' }, res.data.access_token)
      toast.success(`Welcome back, ${res.data.name || email}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Invalid email or password')
    } finally { setLoading(false) }
  }

  async function handleRegister(e) {
    e.preventDefault()
    if (password !== confirm) { toast.error('Passwords do not match'); return }
    if (password.length < 6) { toast.error('Password must be at least 6 characters'); return }
    setLoading(true)
    try {
      const res = await customerRegister({ name, email, password })
      login({ id: res.data.user_id, email, name: res.data.name, role: 'customer' }, res.data.access_token)
      toast.success(`Welcome, ${name}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex flex-col">
      <nav className="flex items-center px-6 py-4">
        <button onClick={() => navigate('/')} className="flex items-center gap-1">
          <span className="text-xl font-black text-indigo-600">Skill</span>
          <span className="text-xl font-black text-gray-800">Sync</span>
        </button>
      </nav>

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">

            {/* Toggle tabs */}
            <div className="flex rounded-xl overflow-hidden border border-gray-200 mb-8">
              <button onClick={() => setMode('login')}
                className={`flex-1 py-2.5 text-sm font-bold transition-colors ${
                  mode === 'login' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                }`}>
                Log In
              </button>
              <button onClick={() => setMode('register')}
                className={`flex-1 py-2.5 text-sm font-bold transition-colors ${
                  mode === 'register' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                }`}>
                Sign Up
              </button>
            </div>

            {mode === 'login' && (
              <>
                <h1 className="text-2xl font-black text-gray-900 mb-1">Customer Login</h1>
                <p className="text-gray-400 text-sm mb-6">Find and hire verified skilled workers near you</p>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                    <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                      placeholder="you@example.com" autoComplete="email"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Password</label>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                      placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" autoComplete="current-password"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <button type="submit" disabled={loading}
                    className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                    {loading ? 'Logging in...' : 'Log In â†’'}
                  </button>
                </form>
                <p className="mt-4 text-center text-xs text-gray-400">
                  No account?{' '}
                  <button onClick={() => setMode('register')} className="text-indigo-600 font-semibold hover:underline">Sign up</button>
                </p>
              </>
            )}

            {mode === 'register' && (
              <>
                <h1 className="text-2xl font-black text-gray-900 mb-1">Create Account</h1>
                <p className="text-gray-400 text-sm mb-6">Join SkillSync to hire verified workers</p>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Full Name</label>
                    <input type="text" value={name} onChange={e => setName(e.target.value)}
                      placeholder="Your full name"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                    <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                      placeholder="you@example.com" autoComplete="email"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Password</label>
                    <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                      placeholder="Min 6 characters" autoComplete="new-password"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">Confirm Password</label>
                    <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)}
                      placeholder="Re-enter password" autoComplete="new-password"
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
                  </div>
                  <button type="submit" disabled={loading}
                    className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                    {loading ? 'Creating account...' : 'Create Account â†’'}
                  </button>
                </form>
                <p className="mt-4 text-center text-xs text-gray-400">
                  Already have an account?{' '}
                  <button onClick={() => setMode('login')} className="text-indigo-600 font-semibold hover:underline">Log in</button>
                </p>
              </>
            )}

            <div className="mt-6 pt-6 border-t border-gray-100 text-center">
              <p className="text-xs text-gray-400 mb-3">Are you a worker? No need to login.</p>
              <button onClick={() => navigate('/ai-call')}
                className="text-orange-500 font-semibold text-sm hover:underline">
                Register as Worker via AI Call â†’
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
