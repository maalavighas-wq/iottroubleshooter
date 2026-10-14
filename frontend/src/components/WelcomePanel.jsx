import React from 'react'

const DEVICES = [
  { id: 'smart_bulb', icon: '💡', label: 'Smart Bulb' },
  { id: 'smart_plug', icon: '🔌', label: 'Smart Plug' },
  { id: 'smart_speaker', icon: '🔊', label: 'Smart Speaker' },
  { id: 'smart_camera', icon: '📷', label: 'Smart Camera' },
  { id: 'other', icon: '📡', label: 'Other Device' },
]

const SUGGESTED = [
  { text: 'My smart bulb is offline', device: 'smart_bulb' },
  { text: "Smart plug won't connect to Wi-Fi", device: 'smart_plug' },
  { text: 'Smart camera keeps disconnecting', device: 'smart_camera' },
  { text: 'My smart speaker setup failed', device: 'smart_speaker' },
  { text: 'Firmware update failed on my device', device: null },
  { text: 'Device not found during pairing', device: null },
]

export default function WelcomePanel({ onDeviceSelect, onSuggestedClick, selectedDevice }) {
  return (
    <div className="space-y-5">
      {/* Welcome card */}
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-5">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-pink-950/80 border border-pink-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h2 className="font-semibold text-white mb-1">How can I help you today?</h2>
            <p className="text-sm text-zinc-400 leading-relaxed">
              I can help diagnose and resolve common smart home device issues — connectivity,
              setup failures, firmware updates, and more. Select a device or describe your problem to get started.
            </p>
          </div>
        </div>
      </div>

      {/* Device selection */}
      <div>
        <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Select Your Device</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
          {DEVICES.map((d) => (
            <button
              key={d.id}
              onClick={() => onDeviceSelect(d.id)}
              className={`flex flex-col items-center gap-1.5 p-3 rounded-lg border text-center transition-all duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-1 focus:ring-offset-black ${
                selectedDevice === d.id
                  ? 'border-pink-500 bg-pink-950/50 shadow-lg shadow-pink-900/20'
                  : 'border-zinc-800 bg-zinc-900 hover:border-pink-700/60 hover:bg-zinc-800'
              }`}
              aria-pressed={selectedDevice === d.id}
            >
              <span className="text-2xl" role="img" aria-label={d.label}>{d.icon}</span>
              <span className={`text-xs font-medium leading-tight ${
                selectedDevice === d.id ? 'text-pink-400' : 'text-zinc-400'
              }`}>{d.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Suggested questions */}
      <div>
        <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Common Issues</h3>
        <div className="flex flex-wrap gap-2">
          {SUGGESTED.map((s, i) => (
            <button
              key={i}
              onClick={() => onSuggestedClick(s.text, s.device)}
              className="text-sm text-pink-300 bg-pink-950/40 border border-pink-900/50 px-3 py-1.5 rounded-full hover:bg-pink-900/50 hover:border-pink-700/60 transition-colors focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-1 focus:ring-offset-black"
            >
              {s.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
