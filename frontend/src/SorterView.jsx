import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'

const BIN_CONFIG = {
  reuse:   { bg: 'bg-green-600',  label: 'REUSE',   icon: '♻️',  text: 'text-white' },
  resale:  { bg: 'bg-blue-600',   label: 'RESALE',  icon: '🏷️',  text: 'text-white' },
  recycle: { bg: 'bg-red-600',    label: 'RECYCLE', icon: '🗑️',  text: 'text-white' },
  flag:    { bg: 'bg-amber-500',  label: 'REVIEW',  icon: '⚠️',  text: 'text-white' },
}

const IDLE = { bg: 'bg-gray-900', label: 'READY', icon: '📦', text: 'text-gray-300' }

export default function SorterView() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [weight, setWeight] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const sessionId = useRef(crypto.randomUUID())

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setResult(data)
      setLoading(false)
    }

    return () => ws.close()
  }, [])

  const handleClassify = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    setLoading(true)
    setResult(null)
    wsRef.current.send(JSON.stringify({
      action: 'classify',
      weight_grams: weight,
      session_id: sessionId.current,
    }))
  }, [weight])

  const current = result ? (BIN_CONFIG[result.bin] || IDLE) : IDLE

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center ${current.bg} transition-colors duration-300`}>
      {/* Status bar */}
      <div className="absolute top-4 right-4 flex items-center gap-2">
        <span className={`w-3 h-3 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-white text-sm opacity-70">{connected ? 'Connected' : 'Offline'}</span>
        <Link to="/ops" className="ml-4 text-white text-sm opacity-60 hover:opacity-100 underline">Ops →</Link>
      </div>

      {/* Main bin display */}
      <div className="flex flex-col items-center gap-6 px-8 text-center">
        <span className="text-9xl select-none">{loading ? '⏳' : current.icon}</span>

        <h1 className={`text-7xl font-black tracking-widest ${current.text}`}>
          {loading ? 'SCANNING…' : current.label}
        </h1>

        {result && (
          <p className={`text-2xl max-w-lg leading-relaxed ${current.text} opacity-90`}>
            {result.reason}
          </p>
        )}

        {result && result.confidence !== undefined && (
          <span className={`text-lg opacity-60 ${current.text}`}>
            Confidence: {Math.round(result.confidence * 100)}%
          </span>
        )}
      </div>

      {/* Weight slider (simulates USB scale) */}
      <div className="absolute bottom-32 left-1/2 -translate-x-1/2 w-80 text-center">
        <label className="text-white opacity-70 text-sm block mb-2">
          Weight: {weight ? `${weight}g` : 'Not set (tap to set)'}
        </label>
        <input
          type="range"
          min="0"
          max="5000"
          step="10"
          value={weight ?? 0}
          onChange={(e) => setWeight(Number(e.target.value) || null)}
          className="w-full h-3 rounded-full appearance-none cursor-pointer"
        />
      </div>

      {/* Classify button — 60px min tap target */}
      <button
        onClick={handleClassify}
        disabled={loading || !connected}
        className="absolute bottom-8 min-h-[64px] px-16 text-2xl font-bold rounded-2xl
                   bg-white text-gray-900 shadow-2xl active:scale-95 transition-transform
                   disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? 'Analysing…' : 'SCAN ITEM'}
      </button>
    </div>
  )
}
