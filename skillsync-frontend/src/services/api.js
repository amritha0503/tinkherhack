import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ─── Auth ───────────────────────────────────────────────────────────────────
export const sendOTP          = (phone)       => api.post('/auth/send-otp', { phone })
export const verifyOTP        = (phone, otp)  => api.post('/auth/verify-otp', { phone, otp })
export const customerRegister = (data)        => api.post('/auth/customer/register', data)
export const customerLogin    = (data)        => api.post('/auth/customer/login', data)

// ─── Workers ────────────────────────────────────────────────────────────────
export const searchWorkers  = (params)      => api.get('/workers/search', { params })
export const getWorker      = (id)          => api.get(`/workers/${id}`)
export const updateWorker   = (id, data)    => api.put(`/workers/${id}`, data)
export const getTrustScore  = (id)          => api.get(`/workers/${id}/trust-score`)
export const getWorkerLedger= (id)          => api.get(`/workers/${id}/ledger`)
export const uploadPhotos   = (id, form)    => api.post(`/workers/${id}/photos`, form, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const uploadVoiceBio = (id, form)    => api.post(`/workers/${id}/voice-bio`, form, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const aadhaarVerify  = (id, data)    => api.post(`/workers/${id}/aadhaar`, data)

// ─── Customers ──────────────────────────────────────────────────────────────
export const registerCustomer = (data)      => api.post('/customers/register', data)
export const getCustomer      = (id)        => api.get(`/customers/${id}`)

// ─── Jobs ───────────────────────────────────────────────────────────────────
export const createJob      = (data)        => api.post('/jobs/create', data)
export const getJob         = (id)          => api.get(`/jobs/${id}`)
export const getWorkerJobs  = (id)          => api.get(`/jobs/worker/${id}`)
export const respondJob     = (id, action)  => api.post(`/jobs/${id}/respond`, { action })
export const completeJob    = (id, data)    => api.post(`/jobs/${id}/complete`, data)
export const disputeJob     = (id, reason)  => api.post(`/jobs/${id}/dispute`, { reason })

// ─── Reviews ────────────────────────────────────────────────────────────────
export const submitReview   = (data)        => api.post('/reviews/submit', data)

// ─── Calls ──────────────────────────────────────────────────────────────────
export const initiateCall   = (data)        => api.post('/calls/initiate', data)
export const endCall        = (callId)      => api.post(`/calls/${callId}/end`)
export const scanQR         = (qrId)        => api.get(`/jobs/qr/${qrId}`)

// ─── Emergency ──────────────────────────────────────────────────────────────
export const triggerEmergency = (data)      => api.post('/emergency/trigger', data)

// ─── AI Call Agent ──────────────────────────────────────────────────────────
export const getLanguages   = ()            => api.get('/ai-call/languages')
export const getQuestions   = (phone, lang) => api.post('/ai-call/questions', { phone, language_key: lang })
export const extractProfile = (data)        => api.post('/ai-call/extract-profile', data)
export const saveProfile    = (phone, profile) => api.post(`/ai-call/save-profile?phone=${phone}`, profile)
export const transcribeVoice= (phone, language, questionKey, audioBlob) => {
  const form = new FormData()
  form.append('phone', phone)
  form.append('language', language)
  form.append('question_key', questionKey)
  form.append('audio', audioBlob, 'recording.webm')
  return api.post('/ai-call/voice-answer', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export default api
