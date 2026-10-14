import React, { useState, useEffect, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import Header from './components/Header.jsx'
import WelcomePanel from './components/WelcomePanel.jsx'
import ChatWindow from './components/ChatWindow.jsx'
import MessageInput from './components/MessageInput.jsx'
import { fetchHealth, sendMessage, sendFeedback } from './api.js'

function getOrCreateSessionId() {
  let sid = sessionStorage.getItem('iot_session_id')
  if (!sid) {
    sid = uuidv4()
    sessionStorage.setItem('iot_session_id', sid)
  }
  return sid
}

export default function App() {
  const [sessionId, setSessionId] = useState(getOrCreateSessionId)
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendStatus, setBackendStatus] = useState('checking')
  const [backendMode, setBackendMode] = useState(null)
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [chatStarted, setChatStarted] = useState(false)

  // Poll health on mount
  useEffect(() => {
    let active = true
    async function check() {
      try {
        const data = await fetchHealth()
        if (active) {
          setBackendStatus(data.status)
          setBackendMode(data.mode)
        }
      } catch {
        if (active) setBackendStatus('error')
      }
    }
    check()
    const interval = setInterval(check, 30000)
    return () => { active = false; clearInterval(interval) }
  }, [])

  const handleSend = useCallback(async (text, overrideDevice) => {
    const device = overrideDevice !== undefined ? overrideDevice : selectedDevice
    setError(null)
    setChatStarted(true)

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setIsLoading(true)

    try {
      const data = await sendMessage({
        message: text,
        sessionId,
        deviceType: device,
      })

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.reply,
        issue_category: data.issue_category,
        current_step: data.current_step,
        total_steps: data.total_steps,
        resolution_status: data.resolution_status,
        sources: data.sources || [],
        is_general_guidance: data.is_general_guidance,
        summary: data.summary || null,
      }])
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Could not reach the backend. Make sure the backend server is running on port 8000.'
      )
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, selectedDevice])

  const handleDeviceSelect = useCallback((deviceId) => {
    setSelectedDevice(prev => prev === deviceId ? null : deviceId)
  }, [])

  const handleSuggestedClick = useCallback((text, device) => {
    if (device) setSelectedDevice(device)
    handleSend(text, device)
  }, [handleSend])

  const handleFeedback = useCallback(async (stepIndex, worked) => {
    // Send the feedback phrase into the chat
    const msg = worked ? 'It works now' : 'Still not working'
    await handleSend(msg)

    // Also POST to feedback endpoint (fire-and-forget)
    sendFeedback({ sessionId, stepIndex: stepIndex || 0, worked }).catch(() => {})
  }, [handleSend, sessionId])

  const handleRestart = useCallback(() => {
    const newSid = uuidv4()
    sessionStorage.setItem('iot_session_id', newSid)
    setSessionId(newSid)
    setMessages([])
    setSelectedDevice(null)
    setChatStarted(false)
    setError(null)
  }, [])

  return (
    <div className="min-h-screen bg-black flex flex-col">
      <Header backendStatus={backendStatus} mode={backendMode} />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-4 sm:py-6 flex flex-col gap-4">
        {/* Welcome panel — shown before chat starts */}
        {!chatStarted && (
          <WelcomePanel
            onDeviceSelect={handleDeviceSelect}
            onSuggestedClick={handleSuggestedClick}
            selectedDevice={selectedDevice}
          />
        )}

        {/* Chat area */}
        <div className={`bg-zinc-950 rounded-xl border border-zinc-800 flex flex-col overflow-hidden ${
          chatStarted ? 'flex-1' : ''
        }`} style={{ minHeight: chatStarted ? '460px' : '320px' }}>
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-zinc-800 bg-zinc-900/60">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-pink-500" />
              <span className="text-xs font-medium text-zinc-500">Troubleshooting Chat</span>
            </div>
            {selectedDevice && (
              <span className="text-xs text-pink-400 bg-pink-950/50 border border-pink-900/40 px-2.5 py-0.5 rounded-full">
                {selectedDevice.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </span>
            )}
          </div>

          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            error={error}
            onFeedback={handleFeedback}
          />

          <MessageInput
            onSend={handleSend}
            disabled={isLoading || backendStatus === 'error'}
            onRestart={handleRestart}
          />
        </div>

        {/* Backend offline notice */}
        {backendStatus === 'error' && (
          <div className="bg-amber-950/50 border border-amber-800/50 rounded-lg p-3 text-sm text-amber-300">
            <strong className="text-amber-400">Backend not connected.</strong> Make sure the FastAPI server is running:
            <code className="ml-1 bg-zinc-900 px-1.5 py-0.5 rounded text-xs font-mono text-pink-300">
              uvicorn main:app --reload --port 8000
            </code>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-900 py-4 text-center text-xs text-zinc-700">
        IoT Troubleshooter &nbsp;·&nbsp; IBM Mini Project &nbsp;·&nbsp;
        <span className="text-zinc-800">Smart Device Assistant v1.0</span>
      </footer>
    </div>
  )
}
