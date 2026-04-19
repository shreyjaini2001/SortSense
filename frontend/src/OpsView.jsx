import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

const BIN_META = {
  reuse:   { icon: '♻️', label: 'Reuse',   color: 'bg-emerald-500', light: 'bg-emerald-50',  text: 'text-emerald-700', desc: 'Shelters & food banks' },
  resale:  { icon: '🏷️', label: 'Resale',  color: 'bg-blue-500',    light: 'bg-blue-50',     text: 'text-blue-700',    desc: 'Goodwill floor' },
  recycle: { icon: '🗑️', label: 'Recycle', color: 'bg-rose-500',    light: 'bg-rose-50',     text: 'text-rose-700',    desc: 'Partner pickup' },
  flag:    { icon: '⚠️', label: 'Review',  color: 'bg-amber-400',   light: 'bg-amber-50',    text: 'text-amber-700',   desc: 'Needs supervisor' },
}

const CAT_META = {
  food:        { icon: '🥫', label: 'Food' },
  clothing:    { icon: '👕', label: 'Clothing' },
  electronics: { icon: '📱', label: 'Electronics' },
  unknown:     { icon: '❓', label: 'Unknown' },
}

async function fetchStats() {
  const res = await fetch('http://localhost:8000/api/v1/stats')
  if (!res.ok) throw new Error('Failed')
  return res.json()
}

export default function OpsView() {
  const { data, isLoading, error, dataUpdatedAt } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 5000,
  })

  const updatedAt = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : null

  const total      = data?.total ?? 0
  const flagRate   = data ? Math.round(data.flag_rate * 100) : 0
  const byBin      = data?.by_bin ?? {}
  const byCat      = data?.by_category ?? {}
  const maxCat     = Math.max(...Object.values(byCat), 1)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="max-w-2xl mx-auto px-6 py-8">

        {/* ── Header ── */}
        <header className="flex items-start justify-between mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Link to="/" className="text-slate-400 hover:text-slate-700 text-sm font-medium transition-colors">
                ← Sorter View
              </Link>
            </div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">Ops Dashboard</h1>
            <p className="text-slate-500 text-sm mt-0.5">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
              {updatedAt && <span className="ml-2 text-emerald-600 font-medium">· Updated {updatedAt}</span>}
            </p>
          </div>
          <div className="flex items-center gap-1.5 bg-emerald-100 text-emerald-700 px-3 py-1.5 rounded-full text-xs font-semibold">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
            Live
          </div>
        </header>

        {isLoading && (
          <div className="text-center py-20 text-slate-400">Loading today's data…</div>
        )}
        {error && (
          <div className="bg-rose-50 text-rose-600 rounded-2xl p-4 text-sm text-center">
            Could not reach backend — is the server running?
          </div>
        )}

        {data && (
          <div className="flex flex-col gap-6">

            {/* ── Hero stats ── */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
                <p className="text-slate-500 text-sm font-medium mb-1">Items Triaged Today</p>
                <p className="text-6xl font-black text-slate-900">{total}</p>
                <p className="text-slate-400 text-xs mt-2">across all categories</p>
              </div>
              <div className={`rounded-2xl p-6 shadow-sm border ${flagRate > 10 ? 'bg-amber-50 border-amber-200' : 'bg-white border-slate-100'}`}>
                <p className="text-slate-500 text-sm font-medium mb-1">Flag Rate</p>
                <p className={`text-6xl font-black ${flagRate > 10 ? 'text-amber-600' : 'text-slate-900'}`}>{flagRate}%</p>
                <p className="text-slate-400 text-xs mt-2">items needing review</p>
              </div>
            </div>

            {/* ── Bin destinations ── */}
            <section>
              <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">
                Bin Destinations
              </h2>
              <div className="flex flex-col gap-2">
                {Object.entries(BIN_META).map(([bin, meta]) => {
                  const count = byBin[bin] ?? 0
                  const pct   = total > 0 ? Math.round((count / total) * 100) : 0
                  return (
                    <div key={bin} className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 flex items-center gap-4">
                      {/* Icon */}
                      <div className={`w-12 h-12 rounded-xl ${meta.light} flex items-center justify-center text-2xl shrink-0`}>
                        {meta.icon}
                      </div>
                      {/* Label + desc */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1.5">
                          <div>
                            <span className={`text-sm font-bold uppercase tracking-wide ${meta.text}`}>{meta.label}</span>
                            <span className="text-slate-400 text-xs ml-2">→ {meta.desc}</span>
                          </div>
                          <span className="text-slate-900 font-black text-xl">{count}</span>
                        </div>
                        {/* Progress bar */}
                        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${meta.color} rounded-full transition-all duration-700`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* ── Category breakdown ── */}
            <section>
              <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">
                Category Mix
              </h2>
              <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 flex flex-col gap-4">
                {Object.entries(CAT_META).map(([cat, meta]) => {
                  const count = byCat[cat] ?? 0
                  const pct   = Math.round((count / maxCat) * 100)
                  return (
                    <div key={cat} className="flex items-center gap-3">
                      <span className="text-xl w-7 shrink-0">{meta.icon}</span>
                      <span className="text-slate-600 text-sm font-medium w-24 shrink-0">{meta.label}</span>
                      <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-slate-400 rounded-full transition-all duration-700"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="text-slate-900 font-bold text-sm w-6 text-right shrink-0">{count}</span>
                    </div>
                  )
                })}
              </div>
            </section>

            {/* ── SDG footer ── */}
            <section className="bg-slate-900 rounded-2xl p-5 flex items-center justify-between">
              <div>
                <p className="text-white font-bold text-sm">Open Source · DPG Standard</p>
                <p className="text-slate-400 text-xs mt-0.5">MIT License · No PII collected</p>
              </div>
              <div className="flex gap-2">
                {['SDG 12', 'SDG 8', 'SDG 11'].map(s => (
                  <span key={s} className="bg-slate-700 text-slate-300 text-xs font-bold px-2.5 py-1 rounded-full">
                    {s}
                  </span>
                ))}
              </div>
            </section>

          </div>
        )}
      </div>
    </div>
  )
}
