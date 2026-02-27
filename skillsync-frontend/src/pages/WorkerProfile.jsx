import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { getWorker, registerWorker, aadhaarVerify, uploadVoiceBio } from '../services/api'
import toast from 'react-hot-toast'
import TrustBadge from '../components/TrustBadge'
import LoadingSpinner from '../components/LoadingSpinner'

const SKILLS = ['Plumber','Electrician','Carpenter','Mason','Painter','Welder','Other']

export default function WorkerProfile() {
  const { user } = useAuth()
  const [worker, setWorker] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [aadhaar, setAadhaar] = useState('')
  const [audioFile, setAudioFile] = useState(null)
  const [form, setForm] = useState({
    name: '', skill_type: '', experience_years: '', daily_rate: '',
    work_radius_km: 10, location_area: '', location_lat: '', location_lng: ''
  })

  useEffect(() => {
    getWorker(user.id)
      .then(({ data }) => {
        setWorker(data)
        setForm({
          name: data.name || '', skill_type: data.skill_type || '',
          experience_years: data.experience_years || '', daily_rate: data.daily_rate || '',
          work_radius_km: data.work_radius_km || 10,
          location_area: data.location_area || '',
          location_lat: data.location_lat || '', location_lng: data.location_lng || ''
        })
      })
      .finally(() => setLoading(false))
  }, [user.id])

  const handleSave = async e => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = { ...form,
        experience_years: form.experience_years ? Number(form.experience_years) : undefined,
        daily_rate: form.daily_rate ? Number(form.daily_rate) : undefined,
        location_lat: form.location_lat ? Number(form.location_lat) : undefined,
        location_lng: form.location_lng ? Number(form.location_lng) : undefined,
      }
      const { data } = await registerWorker(payload)
      toast.success(`Profile saved! Trust score: ${data.trust_score}`)
      const updated = await getWorker(user.id)
      setWorker(updated.data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    } finally { setSaving(false) }
  }

  const handleAadhaar = async () => {
    if (aadhaar.length !== 4) return toast.error('Enter last 4 digits')
    try {
      const { data } = await aadhaarVerify(user.id, aadhaar)
      toast.success(`Aadhaar verified! New score: ${data.new_trust_score}`)
      const updated = await getWorker(user.id)
      setWorker(updated.data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Verification failed')
    }
  }

  const handleVoiceBio = async () => {
    if (!audioFile) return toast.error('Select an audio file')
    const fd = new FormData()
    fd.append('audio', audioFile)
    fd.append('language', 'hi')
    try {
      const { data } = await uploadVoiceBio(user.id, fd)
      toast.success('Voice bio processed by AI!')
      const updated = await getWorker(user.id)
      setWorker(updated.data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-5">
      {/* Trust Score Banner */}
      {worker && (
        <div className="card flex items-center justify-between bg-gradient-to-r from-orange-50 to-yellow-50">
          <div>
            <p className="text-sm text-gray-500">Your Trust Score</p>
            <TrustBadge badge={worker.trust_badge} score={worker.trust_score} />
          </div>
          <div className="text-right text-sm text-gray-500">
            <p>{worker.aadhaar_verified ? '✅ Aadhaar Verified' : '❌ Aadhaar Pending'}</p>
            <p>{worker.profile_complete ? '✅ Profile Complete' : '⚠️ Incomplete'}</p>
          </div>
        </div>
      )}

      {/* Profile Form */}
      <div className="card">
        <h2 className="font-bold text-lg mb-4">📝 Profile Details</h2>
        <form onSubmit={handleSave} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Full Name</label>
              <input className="input" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Ramu Naidu" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Skill</label>
              <select className="input" value={form.skill_type} onChange={e => setForm({...form, skill_type: e.target.value})}>
                <option value="">Select skill</option>
                {SKILLS.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Experience (years)</label>
              <input type="number" className="input" value={form.experience_years} onChange={e => setForm({...form, experience_years: e.target.value})} placeholder="5" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Daily Rate (₹)</label>
              <input type="number" className="input" value={form.daily_rate} onChange={e => setForm({...form, daily_rate: e.target.value})} placeholder="500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Work Radius (km)</label>
              <input type="number" className="input" value={form.work_radius_km} onChange={e => setForm({...form, work_radius_km: e.target.value})} />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Area / Locality</label>
              <input className="input" value={form.location_area} onChange={e => setForm({...form, location_area: e.target.value})} placeholder="Kozhikode" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Latitude</label>
              <input type="number" step="any" className="input" value={form.location_lat} onChange={e => setForm({...form, location_lat: e.target.value})} placeholder="11.2588" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Longitude</label>
              <input type="number" step="any" className="input" value={form.location_lng} onChange={e => setForm({...form, location_lng: e.target.value})} placeholder="75.7804" />
            </div>
          </div>
          <button type="submit" disabled={saving} className="btn-primary w-full">{saving ? 'Saving...' : 'Save Profile'}</button>
        </form>
      </div>

      {/* Aadhaar Verify */}
      <div className="card">
        <h2 className="font-bold text-lg mb-3">🪪 Aadhaar Verification <span className="text-sm text-green-600 font-normal">(+20 trust score)</span></h2>
        <div className="flex gap-2">
          <input className="input" maxLength={4} value={aadhaar} onChange={e => setAadhaar(e.target.value.replace(/\D/g,''))} placeholder="Last 4 digits of Aadhaar" />
          <button onClick={handleAadhaar} className="btn-primary whitespace-nowrap">Verify</button>
        </div>
      </div>

      {/* Voice Bio */}
      <div className="card">
        <h2 className="font-bold text-lg mb-1">🎙️ Voice Bio (AI-powered)</h2>
        <p className="text-xs text-gray-500 mb-3">Upload an audio recording — AI will extract your skills and experience automatically</p>
        <div className="flex gap-2">
          <input type="file" accept="audio/*" onChange={e => setAudioFile(e.target.files[0])} className="input flex-1 text-xs" />
          <button onClick={handleVoiceBio} disabled={!audioFile} className="btn-primary whitespace-nowrap">Upload</button>
        </div>
      </div>
    </div>
  )
}
