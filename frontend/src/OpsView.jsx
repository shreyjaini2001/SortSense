import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

const BIN_COLOURS = {
  reuse:   'bg-green-500',
  resale:  'bg-blue-500',
  recycle: 'bg-red-500',
  flag:    'bg-amber-400',
}

async function fetchStats() {
  const res = await fetch('/api/v1/stats')
  if (!res.ok) throw new Error('Failed to fetch stats')
  return res.json()
}

export default function OpsView() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 5000,
  })

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-4xl font-black">SortSense</h1>
            <p className="text-gray-400 mt-1">Ops Dashboard — refreshes every 5s</p>
          </div>
          <Link to="/" className="text-gray-400 hover:text-white underline text-sm">← Sorter View</Link>
        </div>

        {isLoading && <p className="text-gray-500">Loading stats…</p>}
        {error && <p className="text-red-400">Error loading stats.</p>}

        {data && (
          <>
            {/* Summary */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="bg-gray-800 rounded-2xl p-6">
                <p className="text-gray-400 text-sm">Total Items Today</p>
                <p className="text-5xl font-black mt-1">{data.total}</p>
              </div>
              <div className="bg-gray-800 rounded-2xl p-6">
                <p className="text-gray-400 text-sm">Flag Rate</p>
                <p className="text-5xl font-black mt-1">{Math.round(data.flag_rate * 100)}%</p>
              </div>
            </div>

            {/* Bin breakdown */}
            <h2 className="text-xl font-bold mb-4 text-gray-300">By Bin</h2>
            <div className="grid grid-cols-2 gap-4 mb-8">
              {Object.entries(data.by_bin).map(([bin, count]) => (
                <div key={bin} className="bg-gray-800 rounded-2xl p-6 flex items-center gap-4">
                  <div className={`w-4 h-4 rounded-full ${BIN_COLOURS[bin] || 'bg-gray-500'}`} />
                  <div>
                    <p className="text-gray-400 text-sm uppercase tracking-wide">{bin}</p>
                    <p className="text-3xl font-bold">{count}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Category breakdown */}
            <h2 className="text-xl font-bold mb-4 text-gray-300">By Category</h2>
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(data.by_category).map(([cat, count]) => (
                <div key={cat} className="bg-gray-800 rounded-2xl p-6 text-center">
                  <p className="text-gray-400 text-sm capitalize">{cat}</p>
                  <p className="text-3xl font-bold mt-1">{count}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
