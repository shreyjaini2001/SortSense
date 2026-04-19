import { Link } from 'react-router-dom'

const TECH = [
  {
    layer: 'AI / Vision',
    color: 'border-violet-500 text-violet-400',
    dot: 'bg-violet-500',
    items: [
      { name: 'Featherless AI', desc: 'OpenAI-compatible inference host' },
      { name: 'Qwen3-VL-30B-A3B', desc: 'Multimodal vision — category detection + item analysis' },
      { name: 'EasyOCR', desc: 'Text extraction — expiry dates, model numbers' },
    ],
  },
  {
    layer: 'Backend',
    color: 'border-blue-500 text-blue-400',
    dot: 'bg-blue-500',
    items: [
      { name: 'FastAPI 0.115', desc: 'REST + WebSocket server' },
      { name: 'Python 3.12', desc: 'Runtime' },
      { name: 'SQLAlchemy + SQLite', desc: 'ORM + persistent triage log' },
      { name: 'httpx', desc: 'Async HTTP — external API calls' },
      { name: 'asyncio.gather', desc: 'Parallel vision + OCR execution' },
    ],
  },
  {
    layer: 'Camera',
    color: 'border-zinc-500 text-zinc-400',
    dot: 'bg-zinc-400',
    items: [
      { name: 'imagesnap', desc: 'macOS AVFoundation — JPEG capture via subprocess' },
    ],
  },
  {
    layer: 'External APIs',
    color: 'border-amber-500 text-amber-400',
    dot: 'bg-amber-500',
    items: [
      { name: 'CPSC SaferProducts', desc: 'Electronics recall lookup by model number' },
      { name: 'Open Food Facts v2', desc: 'Expected weight for anomaly detection' },
    ],
  },
  {
    layer: 'Frontend',
    color: 'border-emerald-500 text-emerald-400',
    dot: 'bg-emerald-500',
    items: [
      { name: 'React 18 + Vite 5', desc: 'UI framework + build tool' },
      { name: 'Tailwind CSS 3', desc: 'Utility-first styling' },
      { name: 'React Query', desc: 'Data fetching + 5 s auto-refresh' },
      { name: 'React Router v6', desc: 'Client-side routing' },
      { name: 'Web Speech API', desc: 'Browser-native voice output' },
    ],
  },
]

const APIS = [
  { method: 'GET',  path: '/health',           desc: 'Liveness check — returns status and UTC timestamp.',
    req: null,
    res: '{ "status": "ok", "timestamp": "2026-04-19T…" }' },
  { method: 'POST', path: '/classify',          desc: 'Capture webcam frame via imagesnap and run full triage pipeline.',
    req: '{ "weight_grams": 320, "session_id": "uuid" }',
    res: '{ "category": "food", "bin": "reuse", "confidence": 0.91, "reason": "…", "signals": {…} }' },
  { method: 'POST', path: '/classify/image',    desc: 'Classify from caller-supplied base64 JPEG — tablet UI and tests.',
    req: '{ "b64_image": "…", "weight_grams": null, "session_id": "uuid" }',
    res: '{ "category": "electronics", "bin": "resale", "confidence": 0.85, … }' },
  { method: 'GET',  path: '/api/v1/stats',      desc: "Today's triage counts by bin + category — consumed by Ops dashboard.",
    req: null,
    res: '{ "total": 42, "by_bin": { "reuse": 10, "resale": 25, … }, "flag_rate": 0.07 }' },
  { method: 'GET',  path: '/api/v1/export',     desc: 'Full session export as JSON — DPG Indicator 6 open data portability.',
    req: null,
    res: '{ "export_date": "2026-04-19", "total_items": 42, "items": [ … ] }' },
  { method: 'WS',   path: '/ws',                desc: 'Real-time bidirectional channel — send classify action, receive result.',
    req: '{ "action": "classify", "weight_grams": null, "b64_image": "…", "session_id": "uuid" }',
    res: '{ "category": "clothing", "bin": "resale", "confidence": 0.88, "reason": "…" }' },
]

const METHOD_STYLE = {
  GET:  'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40',
  POST: 'bg-blue-500/20 text-blue-300 border border-blue-500/40',
  WS:   'bg-violet-500/20 text-violet-300 border border-violet-500/40',
}

const FLOW = [
  { icon: '📷', label: 'Camera', sub: 'imagesnap · macOS AVFoundation · JPEG → base64', color: 'bg-zinc-800 border-zinc-600' },
  { icon: '⚡', label: 'FastAPI Backend', sub: 'WebSocket /ws · REST endpoints · Python 3.12', color: 'bg-slate-800 border-slate-600' },
  { icon: '🤖', label: 'Category Detection', sub: 'Featherless AI · Qwen3-VL-30B · food / clothing / electronics / general', color: 'bg-violet-900/50 border-violet-500' },
  { icon: '🔀', label: 'Category Router', sub: 'Food pipeline · Clothing pipeline · Electronics pipeline · General pipeline', color: 'bg-blue-900/50 border-blue-500', wide: true },
  { icon: '⚙️', label: 'Signal Enrichment', sub: 'Vision analysis + EasyOCR + CPSC / Open Food Facts APIs · parallel asyncio', color: 'bg-amber-900/50 border-amber-500', wide: true },
  { icon: '🗄️', label: 'SQLite Logging', sub: 'TriageLog · SQLAlchemy · every scan persisted · swappable to Postgres', color: 'bg-zinc-800 border-zinc-600' },
  { icon: '📱', label: 'React Frontend', sub: 'Sorter UI · Ops Dashboard · Arch view · React 18 + Tailwind + React Query', color: 'bg-emerald-900/50 border-emerald-500', wide: true },
  { icon: '🔊', label: 'Voice Output', sub: 'Web Speech API · bin label + reason spoken aloud · no SDK required', color: 'bg-sky-900/50 border-sky-500' },
]

export default function ArchView() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Nav */}
      <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-white/10">
        <span className="font-black text-lg tracking-tight">SortSense</span>
        <div className="flex gap-5 text-sm">
          <Link to="/" className="text-white/40 hover:text-white transition-colors">Sorter</Link>
          <Link to="/ops" className="text-white/40 hover:text-white transition-colors">Ops</Link>
          <span className="text-white font-semibold">Architecture</span>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-12 space-y-20">

        {/* ── FLOW DIAGRAM ─────────────────────────────────────────── */}
        <section>
          <h2 className="text-2xl font-black mb-1">System Flow</h2>
          <p className="text-white/40 text-sm mb-8">End-to-end pipeline — top to bottom</p>

          <div className="flex flex-col items-center gap-0">
            {FLOW.map((node, i) => (
              <div key={node.label} className="flex flex-col items-center w-full">
                {/* Node */}
                <div className={`border rounded-xl px-5 py-4 text-center w-full max-w-md ${node.color}`}>
                  <div className="text-3xl mb-1">{node.icon}</div>
                  <div className="font-bold text-base">{node.label}</div>
                  <div className="text-xs text-white/50 mt-1 leading-relaxed">{node.sub}</div>
                </div>
                {/* Arrow — not after last node */}
                {i < FLOW.length - 1 && (
                  <div className="flex flex-col items-center py-1">
                    <div className="w-px h-6 bg-white/20" />
                    <div className="text-white/30 text-xs">▼</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* ── TECH STACK ───────────────────────────────────────────── */}
        <section>
          <h2 className="text-2xl font-black mb-1">Tech Stack</h2>
          <p className="text-white/40 text-sm mb-8">Every dependency in the system</p>

          <div className="space-y-6">
            {TECH.map(({ layer, color, dot, items }) => (
              <div key={layer}>
                <div className={`flex items-center gap-2 text-xs font-bold tracking-widest uppercase mb-3 ${color}`}>
                  <span className={`w-2 h-2 rounded-full ${dot}`} />
                  {layer}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {items.map(({ name, desc }) => (
                    <div key={name} className="bg-white/5 border border-white/8 rounded-lg px-4 py-3 flex flex-col gap-0.5">
                      <span className="text-white font-semibold text-sm">{name}</span>
                      <span className="text-white/40 text-xs">{desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── API REFERENCE ────────────────────────────────────────── */}
        <section>
          <h2 className="text-2xl font-black mb-1">API Reference</h2>
          <p className="text-white/40 text-sm mb-8">All endpoints — FastAPI backend on port 8000</p>

          <div className="space-y-3">
            {APIS.map(({ method, path, desc, req, res }) => (
              <div key={path} className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <div className="flex items-center gap-3 px-5 py-3 border-b border-white/8">
                  <span className={`text-xs font-black px-2 py-0.5 rounded font-mono ${METHOD_STYLE[method]}`}>
                    {method}
                  </span>
                  <code className="text-white font-mono text-sm">{path}</code>
                </div>
                <div className="px-5 py-4 space-y-3">
                  <p className="text-white/60 text-sm">{desc}</p>
                  {req && (
                    <div>
                      <div className="text-xs text-white/25 uppercase tracking-widest mb-1.5">Request body</div>
                      <pre className="bg-black/40 rounded-lg px-4 py-2.5 text-xs text-emerald-300 overflow-x-auto">{req}</pre>
                    </div>
                  )}
                  <div>
                    <div className="text-xs text-white/25 uppercase tracking-widest mb-1.5">Response</div>
                    <pre className="bg-black/40 rounded-lg px-4 py-2.5 text-xs text-sky-300 overflow-x-auto">{res}</pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="text-center text-white/20 text-xs pb-4">
          SortSense · MIT License · SDG 12 · SDG 8 · SDG 11
        </div>

      </div>
    </div>
  )
}
