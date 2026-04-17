import { useState } from "react"
import { getSeasonComparison } from "../api/client"
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from "recharts"

const CONSTRUCTORS = [
  "Red Bull", "Mercedes", "Ferrari", "McLaren",
  "Aston Martin", "Alpine F1 Team", "Williams", "Haas F1 Team",
]

const DIMENSIONS = [
  { key: "bvi",        label: "Composite BVI" },
  { key: "perf_score", label: "Performance" },
  { key: "cons_score", label: "Consistency" },
  { key: "expo_score", label: "Exposure" },
]

const COLORS = [
  "#C8102E", "#00D2BE", "#DC0000", "#FF8000",
  "#006F62", "#0090FF", "#005AFF", "#B6BABD",
]

export default function SeasonComparison() {
  const [selected, setSelected]   = useState(["Red Bull", "Mercedes"])
  const [dimension, setDimension] = useState("bvi")
  const [datasets, setDatasets]   = useState({})
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)

  const toggleConstructor = (name) => {
    setSelected((prev) =>
      prev.includes(name)
        ? prev.filter((c) => c !== name)
        : [...prev, name]
    )
  }

  const fetchAll = () => {
    setLoading(true)
    setError(null)
    Promise.all(
      selected.map((c) =>
        getSeasonComparison(c).then((res) => ({ name: c, trends: res.trends }))
      )
    )
      .then((results) => {
        const map = {}
        results.forEach(({ name, trends }) => { map[name] = trends })
        setDatasets(map)
      })
      .catch(() => setError("Failed to load season trends."))
      .finally(() => setLoading(false))
  }

  // Merge into chart-friendly format [{season, Red Bull: 82, Mercedes: 59, ...}]
  const seasons = [2018, 2019, 2020, 2021, 2022, 2023]
  const chartData = seasons.map((yr) => {
    const row = { season: yr }
    Object.entries(datasets).forEach(([name, trends]) => {
      const point = trends.find((t) => t.season === yr)
      row[name] = point ? point[dimension] : null
    })
    return row
  })

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Season Comparison</h1>
        <p className="text-sm text-gray-500 mt-1">
          Year-over-year BVI trajectory across constructors
        </p>
      </div>

      {/* Constructor picker */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
        <p className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
          Select constructors
        </p>
        <div className="flex flex-wrap gap-2 mb-4">
          {CONSTRUCTORS.map((c, i) => (
            <button
              key={c}
              onClick={() => toggleConstructor(c)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                selected.includes(c)
                  ? "text-white border-transparent"
                  : "border-gray-200 text-gray-500 hover:border-gray-400"
              }`}
              style={selected.includes(c)
                ? { background: COLORS[CONSTRUCTORS.indexOf(c) % COLORS.length] }
                : {}
              }
            >
              {c}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <div>
            <label className="text-xs font-mono text-gray-400 mr-2">Dimension:</label>
            <select
              value={dimension}
              onChange={(e) => setDimension(e.target.value)}
              className="text-xs font-mono border border-gray-200 rounded px-2 py-1 text-gray-600"
            >
              {DIMENSIONS.map((d) => (
                <option key={d.key} value={d.key}>{d.label}</option>
              ))}
            </select>
          </div>
          <button
            onClick={fetchAll}
            disabled={loading || selected.length === 0}
            className="ml-auto bg-f1red text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-f1red-dark transition-colors disabled:opacity-50"
          >
            {loading ? "Loading…" : "Load trends"}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      {Object.keys(datasets).length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis
                dataKey="season"
                tick={{ fontSize: 11, fontFamily: "DM Mono", fill: "#9ca3af" }}
              />
              <YAxis
                domain={[0, 105]}
                tick={{ fontSize: 11, fontFamily: "DM Mono", fill: "#9ca3af" }}
              />
              <ReferenceLine y={75} stroke="#22c55e" strokeDasharray="4 4" label={{ value: "Tier 1", fontSize: 10, fill: "#22c55e" }} />
              <ReferenceLine y={50} stroke="#f97316" strokeDasharray="4 4" label={{ value: "Tier 2", fontSize: 10, fill: "#f97316" }} />
              <Tooltip
                contentStyle={{ fontSize: 12, fontFamily: "DM Mono", borderRadius: 8, border: "1px solid #e5e7eb" }}
                formatter={(v) => v !== null ? v.toFixed(1) : "N/A"}
              />
              <Legend wrapperStyle={{ fontSize: 12, fontFamily: "DM Mono" }} />
              {Object.keys(datasets).map((name, i) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={COLORS[CONSTRUCTORS.indexOf(name) % COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {Object.keys(datasets).length === 0 && !loading && (
        <div className="text-center py-20 text-gray-400 text-sm">
          Select constructors and click Load trends.
        </div>
      )}
    </div>
  )
}
