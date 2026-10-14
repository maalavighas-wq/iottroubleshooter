import React, { useState } from 'react'

export default function MessageInput({ onSend, disabled, onRestart }) {
  const [value, setValue] = useState('')

  function handleSend() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="bg-zinc-950 border-t border-zinc-800 px-4 py-3">
      <div className="flex items-end gap-2">
        {/* Restart button */}
        <button
          onClick={onRestart}
          title="Restart troubleshooting"
          className="flex-shrink-0 w-9 h-9 flex items-center justify-center rounded-lg border border-zinc-800 text-zinc-600 hover:text-pink-400 hover:border-pink-800 hover:bg-pink-950/30 transition-colors focus:outline-none focus:ring-2 focus:ring-pink-500"
          aria-label="Restart troubleshooting"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        {/* Text area */}
        <div className="flex-1 relative">
          <textarea
            rows={1}
            value={value}
            onChange={(e) => {
              setValue(e.target.value)
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
            }}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Describe your IoT device issue…"
            className="w-full resize-none rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-gray-200 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent disabled:bg-zinc-900/50 disabled:cursor-not-allowed overflow-hidden leading-relaxed"
            style={{ minHeight: '42px', maxHeight: '120px' }}
            aria-label="Type your message"
          />
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!value.trim() || disabled}
          className="flex-shrink-0 w-9 h-9 flex items-center justify-center rounded-lg bg-pink-600 text-white hover:bg-pink-500 disabled:bg-zinc-800 disabled:text-zinc-600 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-1 focus:ring-offset-black shadow-md shadow-pink-900/30"
          aria-label="Send message"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      <p className="text-xs text-zinc-700 mt-1.5 text-center">
        Press <kbd className="px-1 py-0.5 bg-zinc-800 border border-zinc-700 rounded text-xs text-zinc-400">Enter</kbd> to send &nbsp;·&nbsp;
        <button onClick={onRestart} className="underline hover:text-pink-400 transition-colors focus:outline-none">Restart troubleshooting</button>
      </p>
    </div>
  )
}
