import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'

const BIN = {
  reuse: {
    bg: 'bg-emerald-500',
    label: 'GREEN BIN',
    name: 'REUSE',
    icon: '♻️',
    why: null,
  },
  resale: {
    bg: 'bg-blue-500',
    label: 'BLUE BIN',
    name: 'RESALE',
    icon: '🏷️',
    why: null,
  },
  recycle: {
    bg: 'bg-rose-500',
    label: 'RED BIN',
    name: 'RECYCLE',
    icon: '🗑️',
    why: null,
  },
  flag: {
    bg: 'bg-amber-400',
    label: 'HOLD',
    name: 'GET SUPERVISOR',
    icon: '⚠️',
    why: null,
  },
}

// Trim to first sentence, max 120 chars
function firstSentence(text) {
  if (!text) return ''
  const s = text.split(/\.\s+/)[0].replace(/\.$/, '') + '.'
  return s.length > 140 ? s.slice(0, 137) + '…' : s
}

export default function SorterView() {
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [connected, setConnected] = useState(false)
  const [weight, setWeight]     = useState(0)
  const [showScale, setShowScale] = useState(false)
  const wsRef     = useRef(null)
  const sessionId = useRef(crypto.randomUUID())

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`)
    wsRef.current = ws
    ws.onopen    = () => setConnected(true)
    ws.onclose   = () => setConnected(false)
    ws.onmessage = (e) => { setResult(JSON.parse(e.data)); setLoading(false) }
    return () => ws.close()
  }, [])

  const scan = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    setLoading(true)
    setResult(null)
    wsRef.current.send(JSON.stringify({
      action: 'classify',
      weight_grams: weight > 0 ? weight : null,
      session_id: sessionId.current,
    }))
  }, [weight])

  const bin = result ? (BIN[result.bin] || BIN.flag) : null
  const isFood = result?.category === 'food'

  // ── IDLE ──────────────────────────────────────────────────────────────
  if (!result && !loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col">
        {/* Top bar */}
        <div className="flex items-center justify-between px-6 pt-5">
          <span className="text-white font-black text-lg tracking-tight">SortSense</span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="text-white/40 text-xs">{connected ? 'Live' : 'Offline'}</span>
            </div>
            <Link to="/ops" className="text-white/30 hover:text-white/70 text-xs transition-colors">
              Ops →
            </Link>
          </div>
        </div>

        {/* Center */}
        <div className="flex-1 flex flex-col items-center justify-center gap-6 px-8 text-center">
          <span className="text-8xl">📦</span>
          <div>
            <h1 className="text-4xl font-black text-white">Ready to Scan</h1>
            <p className="text-white/50 text-lg mt-2">Place item in front of camera, then tap Scan</p>
          </div>

          {/* Three bin legend */}
          <div className="flex gap-3 mt-2">
            {[
              { color: 'bg-emerald-500', label: 'Green = Reuse' },
              { color: 'bg-blue-500',    label: 'Blue = Resale' },
              { color: 'bg-rose-500',    label: 'Red = Recycle' },
            ].map(b => (
              <div key={b.label} className="flex items-center gap-2 bg-white/5 rounded-full px-3 py-1.5">
                <span className={`w-3 h-3 rounded-full ${b.color} shrink-0`} />
                <span className="text-white/60 text-xs font-medium">{b.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom */}
        <div className="px-6 pb-8 flex flex-col gap-3">
          {/* Food scale toggle — only visible if needed */}
          <button
            onClick={() => setShowScale(s => !s)}
            className="text-white/30 text-xs text-center hover:text-white/60 transition-colors"
          >
            {showScale ? '▾ Hide food scale' : '⚖️ Set food item weight (optional)'}
          </button>

          {showScale && (
            <div className="bg-white/5 rounded-2xl px-5 py-4">
              <div className="flex justify-between text-white/60 text-sm mb-2">
                <span>Food Scale (simulated)</span>
                <span className="font-bold text-white">{weight > 0 ? `${weight} g` : '— g'}</span>
              </div>
              <input
                type="range" min="0" max="5000" step="50" value={weight}
                onChange={e => setWeight(Number(e.target.value))}
                className="w-full accent-white cursor-pointer"
              />
              <div className="flex justify-between text-white/20 text-xs mt-1">
                <span>0 g</span><span>5 kg</span>
              </div>
            </div>
          )}

          <button
            onClick={scan}
            disabled={!connected}
            className="w-full h-16 rounded-2xl font-black text-xl bg-white text-slate-900
                       shadow-2xl active:scale-95 transition-all duration-150
                       disabled:opacity-30 disabled:cursor-not-allowed"
          >
            📸  SCAN ITEM
          </button>
        </div>
      </div>
    )
  }

  // ── SCANNING ─────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-6">
        <span className="text-8xl animate-pulse">🔍</span>
        <h1 className="text-4xl font-black text-white">Scanning…</h1>
        <p className="text-white/40 text-lg">AI is analysing the item</p>
      </div>
    )
  }

  // ── RESULT ────────────────────────────────────────────────────────────
  return (
    <div className={`min-h-screen ${bin.bg} flex flex-col transition-all duration-500`}>

      {/* Top bar — minimal */}
      <div className="flex items-center justify-between px-6 pt-5">
        <span className="text-white/60 font-bold text-sm tracking-tight">SortSense</span>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-white/40 animate-pulse" />
            <span className="text-white/40 text-xs">Live</span>
          </div>
          <Link to="/ops" className="text-white/30 hover:text-white/60 text-xs transition-colors">Ops →</Link>
        </div>
      </div>

      {/* Main result — full screen focus */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 text-center gap-6">

        {/* Big icon */}
        <span className="text-9xl drop-shadow-lg">{bin.icon}</span>

        {/* Bin label + name */}
        <div>
          <p className="text-white/70 text-xl font-bold tracking-widest uppercase mb-1">
            {bin.label}
          </p>
          <h1 className="text-7xl font-black text-white tracking-tight leading-none drop-shadow">
            {bin.name}
          </h1>
        </div>

        {/* Plain English reason — one sentence */}
        <p className="text-white text-xl font-medium max-w-sm leading-relaxed bg-black/20 rounded-2xl px-6 py-4">
          {firstSentence(result.reason)}
        </p>

        {/* Food scale weight anomaly note if relevant */}
        {isFood && result.signals?.weight_anomaly && (
          <p className="text-white/70 text-sm">⚖️ Weight anomaly detected</p>
        )}
      </div>

      {/* Scan next */}
      <div className="px-6 pb-8 pt-4">
        <button
          onClick={() => { setResult(null); setWeight(0) }}
          className="w-full h-16 rounded-2xl font-black text-xl
                     bg-black/20 text-white border-2 border-white/30
                     hover:bg-black/30 active:scale-95 transition-all duration-150"
        >
          📸  SCAN NEXT ITEM
        </button>
      </div>
    </div>
  )
}
