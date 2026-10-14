import React from 'react'

function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br />')
}

function UserBubble({ message }) {
  return (
    <div className="flex justify-end mb-4">
      <div className="max-w-xs sm:max-w-md lg:max-w-lg">
        <div className="bg-pink-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed shadow-lg shadow-pink-900/30">
          {message.content}
        </div>
        <p className="text-xs text-zinc-600 mt-1 text-right">You</p>
      </div>
    </div>
  )
}

function AssistantBubble({ message, onFeedback, stepIndex }) {
  const isResolved = message.resolution_status === 'resolved'
  const isUnresolved = message.resolution_status === 'unresolved'
  const hasSummary = message.summary
  const hasSources = message.sources && message.sources.length > 0
  const isGeneral = message.is_general_guidance

  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-start gap-2.5 max-w-xs sm:max-w-md lg:max-w-xl">
        {/* Avatar */}
        <div className="w-7 h-7 bg-pink-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md shadow-pink-900/40">
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
          </svg>
        </div>

        <div className="flex-1 space-y-2">
          {/* Main message bubble */}
          <div className={`px-4 py-3 rounded-2xl rounded-tl-sm text-sm leading-relaxed ${
            isResolved
              ? 'bg-emerald-950/70 border border-emerald-800/60 text-emerald-200'
              : isUnresolved
                ? 'bg-amber-950/60 border border-amber-800/50 text-amber-200'
                : 'bg-zinc-900 border border-zinc-800 text-gray-200'
          }`}>
            <p
              dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
              className="[&>strong]:font-semibold [&>strong]:text-pink-300"
            />
          </div>

          {/* Step progress bar */}
          {message.total_steps > 0 && message.current_step > 0 && !hasSummary && (
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-zinc-800 rounded-full h-1">
                <div
                  className="bg-pink-500 h-1 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (message.current_step / message.total_steps) * 100)}%` }}
                />
              </div>
              <span className="text-xs text-zinc-500">
                Step {message.current_step}/{message.total_steps}
              </span>
            </div>
          )}

          {/* Feedback action buttons */}
          {!hasSummary && message.resolution_status === 'in_progress' && message.current_step > 0 && (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => onFeedback && onFeedback(stepIndex, true)}
                className="inline-flex items-center gap-1 text-xs bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 px-3 py-1.5 rounded-full hover:bg-emerald-900/40 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                It worked
              </button>
              <button
                onClick={() => onFeedback && onFeedback(stepIndex, false)}
                className="inline-flex items-center gap-1 text-xs bg-red-950/60 text-red-400 border border-red-800/50 px-3 py-1.5 rounded-full hover:bg-red-900/40 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Still not working
              </button>
            </div>
          )}

          {/* Summary card */}
          {hasSummary && (
            <div className={`rounded-lg border p-3 text-xs space-y-1 ${
              isResolved
                ? 'bg-emerald-950/50 border-emerald-800/50'
                : 'bg-amber-950/50 border-amber-800/50'
            }`}>
              <p className="font-semibold text-pink-300 mb-1.5">Diagnosis Summary</p>
              <p><span className="text-zinc-500">Device:</span> <span className="font-medium text-zinc-200">{message.summary.device}</span></p>
              <p><span className="text-zinc-500">Issue Type:</span> <span className="font-medium text-zinc-200 capitalize">{message.summary.issue_category}</span></p>
              {message.summary.symptoms?.length > 0 && (
                <p><span className="text-zinc-500">Symptoms:</span> <span className="text-zinc-300">{message.summary.symptoms.slice(0, 2).join('; ')}</span></p>
              )}
              {message.summary.attempted_steps?.length > 0 && (
                <div>
                  <p className="text-zinc-500 mb-0.5">Steps Attempted:</p>
                  <ol className="list-decimal list-inside space-y-0.5">
                    {message.summary.attempted_steps.map((s, i) => (
                      <li key={i} className="text-zinc-300 leading-snug"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(s) }} />
                    ))}
                  </ol>
                </div>
              )}
              <p><span className="text-zinc-500">Outcome:</span> <span className={`font-semibold ${isResolved ? 'text-emerald-400' : 'text-amber-400'}`}>
                {isResolved ? 'Resolved' : 'Unresolved'}
              </span></p>
            </div>
          )}

          {/* Sources */}
          {hasSources && (
            <div className="mt-1">
              <p className="text-xs text-zinc-600 mb-1">
                {isGeneral ? 'General guidance' : 'From knowledge base:'}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {message.sources.map((src, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 text-xs bg-pink-950/40 text-pink-400 border border-pink-900/40 px-2 py-0.5 rounded-full"
                    title={`Relevance: ${Math.round(src.relevance * 100)}%`}
                  >
                    <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {src.title}
                  </span>
                ))}
              </div>
            </div>
          )}

          <p className="text-xs text-zinc-700">IoT Troubleshooter</p>
        </div>
      </div>
    </div>
  )
}

function LoadingBubble() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-start gap-2.5">
        <div className="w-7 h-7 bg-pink-600 rounded-full flex items-center justify-center flex-shrink-0">
          <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
          </svg>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 px-4 py-3 rounded-2xl rounded-tl-sm">
          <div className="flex gap-1 items-center">
            <span className="w-1.5 h-1.5 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  )
}

function ErrorBubble({ error }) {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-red-950/60 border border-red-800/50 text-red-300 text-sm px-4 py-3 rounded-2xl rounded-tl-sm max-w-sm">
        <p className="font-medium mb-0.5 text-red-400">Connection Error</p>
        <p className="text-xs text-red-500">{error}</p>
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, isLoading, error, onFeedback }) {
  const endRef = React.useRef(null)

  React.useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 chat-scrollbar" aria-live="polite" aria-label="Chat conversation">
      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full text-center py-12">
          <div className="w-14 h-14 bg-zinc-900 border border-zinc-800 rounded-full flex items-center justify-center mb-3">
            <svg className="w-7 h-7 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <p className="text-zinc-500 text-sm">Select a device above or type your question to begin.</p>
        </div>
      )}
      {messages.map((msg, i) => {
        if (msg.role === 'user') {
          return <UserBubble key={i} message={msg} />
        }
        return (
          <AssistantBubble
            key={i}
            message={msg}
            stepIndex={msg.current_step}
            onFeedback={onFeedback}
          />
        )
      })}
      {isLoading && <LoadingBubble />}
      {error && <ErrorBubble error={error} />}
      <div ref={endRef} />
    </div>
  )
}
