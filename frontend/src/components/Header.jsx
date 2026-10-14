import React from 'react'

export default function Header({ backendStatus, mode }) {
  const isOnline = backendStatus === 'ok'

  return (
    <header className="bg-zinc-950 border-b border-zinc-800 sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
        {/* Logo + Title */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-pink-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg shadow-pink-900/40">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-semibold text-white leading-tight">IoT Troubleshooter</h1>
            <p className="text-xs text-zinc-400 leading-tight">Smart Device Assistant</p>
          </div>
        </div>

        {/* Status indicators */}
        <div className="flex items-center gap-3">
          {mode && (
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs text-pink-300 bg-pink-950/60 border border-pink-900/50 px-2.5 py-1 rounded-full">
              <svg className="w-3 h-3 text-pink-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
              </svg>
              {mode === 'rule_based' ? 'Demo Mode' : 'IBM watsonx'}
            </span>
          )}
          <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${
            isOnline
              ? 'bg-emerald-950/60 text-emerald-400 border-emerald-900/50'
              : 'bg-red-950/60 text-red-400 border-red-900/50'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-emerald-400' : 'bg-red-500'}`} />
            {isOnline ? 'Connected' : 'Offline'}
          </span>
          <span className="text-xs text-zinc-600 hidden md:block">IBM Mini Project</span>
        </div>
      </div>
    </header>
  )
}
