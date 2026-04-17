import { useState } from "react"
import { getCircuitPerformance } from "../api/client"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts"

const CIRCUITS = [
  { id: 6,  name: "Monaco" },
  { id: 9,  name: "Silverstone" },
  { id: 13, name: "Spa-Francorchamps" },
  { id: 10, name: "Monza" },
  { id: 1,  name: "Melbourne" },
  { id: 24, name: "Bahrain" },
  { id: 70, name: "Zandvoort" },
  { id: 73, name: "Jeddah" },
]

export default function CircuitIntelligence() {
  const [circuitId, setCircuitId] = useState(6)
  const [data, setData]           = useState([])
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [metric, setMetric]       = useState("win_rate")

  const fetch = () => {
    setLoading(true)
    setError(null)
    getCircuitPerformance(circuitId)
      .then((res) => setData(res || []))
      .catch(() => setError("No data for this circuit."))
      .finally(() => setLoading(false))
  }

  const chartData = [...data]
    .sort((a, b) => b[metric] - a[metric])
    .slice(0, 10)
    .map((r) => ({ name: r.constructor, value: r[metric] }))

  const METRIC_LABELS = {
    win_rate:   "Win rate",
    avg_finish: "Avg finish position (lower = better)",
    races:      "Total races",
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Circuit Intelligence</h1>
        <p className="text-sm text-gray-500 mt-1">
          Constructor performance stats by venue
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-2">Circuit</label>
            <select
              value={circuitId}
              onChange={(e) => setCircuitId(Number(e.target.value))}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700"
            >
              {CIRCUITS.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-2">Metric</label>
            <select
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700"
            >
              {Object.entries(METRIC_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={fetch}
              disabled={loading}
              className="w-full bg-f1red text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-f1red-dark transition-colors disabled:opacity-50"
            >
              {loading ? "Loading…" : "Load circuit"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>
      )}

      {data.length > 0 && (
        <div className="space-y-5">
          {/* Chart */}
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <p className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-4">
              {METRIC_LABELS[metric]} — top 10 constructors
            </p>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 0, right: 20, bottom: 0, left: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fontFamily: "DM Mono", fill: "#9ca3af" }} />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fontSize: 11, fontFamily: "DM Mono", fill: "#6b7280" }}
                  width={80}
                />
                <Tooltip
                  contentStyle={{ fontSize: 12, fontFamily: "DM Mono", borderRadius: 8, border: "1px solid #e5e7eb" }}
                  formatter={(v) => [
                    metric === "win_rate" ? `${(v * 100).toFixed(1)}%` : v.toFixed(2),
                    METRIC_LABELS[metric],
                  ]}
                />
                <Bar dataKey="value" fill="#C8102E" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {["Constructor", "Races", "Wins", "Podiums", "Win rate", "Avg finish"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-mono text-gray-400 uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.sort((a, b) => b.win_rate - a.win_rate).map((r) => (
                  <tr key={r.constructor} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{r.constructor}</td>
                    <td className="px-4 py-3 font-mono text-gray-600">{r.races}</td>
                    <td className="px-4 py-3 font-mono text-gray-600">{r.wins}</td>
                    <td className="px-4 py-3 font-mono text-gray-600">{r.podiums}</td>
                    <td className="px-4 py-3 font-mono text-gray-600">{(r.win_rate * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3 font-mono text-gray-600">{r.avg_finish.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data.length === 0 && !loading && !error && (
        <div className="text-center py-20 text-gray-400 text-sm">
          Select a circuit and click Load circuit.
        </div>
      )}
    </div>
  )
}
