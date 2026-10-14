import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchHealth() {
  const res = await api.get('/health')
  return res.data
}

export async function fetchDevices() {
  const res = await api.get('/devices')
  return res.data
}

export async function sendMessage({ message, sessionId, deviceType }) {
  const res = await api.post('/chat', {
    message,
    session_id: sessionId,
    device_type: deviceType || null,
  })
  return res.data
}

export async function sendFeedback({ sessionId, stepIndex, worked, message }) {
  const res = await api.post('/feedback', {
    session_id: sessionId,
    step_index: stepIndex,
    worked,
    message: message || null,
  })
  return res.data
}
