import { useState, useEffect } from "react"
import { getConstructorRankings } from "../api/client"
import TierBadge from "../components/TierBadge"
import ScoreBar from "../components/ScoreBar"

const SEASONS = [2018, 2019, 2020, 2021, 2022, 2023]

export default function ConstructorRankings() {
  const [season, setSeason]   = useState(2023)
  const [data, setData]       = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [sortBy, setSortBy]   = useState("bvi")

  useEffect(() => {
    setLoading(true)
    setError(null)
    getConstructorRankings(season)
      .then((res) => setData(res.results || []))
      .catch(() => setError("Failed to load rankings."))
      .finally(() => setLoading(false))
  }, [season])

  const sorted = [...data].sort((a, b) => b[sortBy] - a[sortBy])

  const COLS = [
    { label: "Pos",         key: "championship_pos" },
    { label: "Constructor", key: null },
    { label: "BVI",         key: "bvi" },
    { label: "Points",      key: "total_points" },
    { label: "Wins",        key: "wins" },
    { label: "Podiums",     key: "podiums" },
    { label: "Tier",        key: null },
    { label: "Perf",        key: "perf_score" },
    { label: "Cons",        key: "cons_score" },
    { label: "Expo",        key: "expo_score" },
  ]

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Constructor Rankings</h1>
        <p className="text-sm text-gray-500 mt-1">
          Championship standings with ML-adjusted BVI metrics
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        <div className="flex gap-2">
          {SEASONS.map((yr) => (
            <button
              key={yr}
              onClick={() => setSeason(yr)}
              className={`px-3 py-1 rounded text-sm font-mono border transition-colors ${
                season === yr
                  ? "bg-f1red text-white border-f1red"
                  : "border-gray-200 text-gray-500 hover:border-gray-400"
              }`}
            >
              {yr}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs text-gray-400 font-mono">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="text-xs font-mono border border-gray-200 rounded px-2 py-1 text-gray-600"
          >
            <option value="bvi">BVI</option>
            <option value="total_points">Points</option>
            <option value="wins">Wins</option>
            <option value="perf_score">Performance</option>
            <option value="cons_score">Consistency</option>
            <option value="expo_score">Exposure</option>
          </select>
        </div>
      </div>

      {loading && <div className="text-center py-20 text-gray-400 text-sm">Loading…</div>}
      {error   && <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>}

      {!loading && !error && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                {COLS.map((col) => (
                  <th
                    key={col.label}
                    onClick={() => col.key && setSortBy(col.key)}
                    className={`px-4 py-3 text-left text-xs font-mono text-gray-400 uppercase tracking-wider
                      ${col.key ? "cursor-pointer hover:text-gray-700" : ""}
                      ${sortBy === col.key ? "text-f1red" : ""}`}
                  >
                    {col.label}
                    {sortBy === col.key && " ↓"}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {sorted.map((r) => (
                <tr key={r.constructor_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-gray-400 text-xs">{r.championship_pos}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{r.constructor}</td>
                  <td className="px-4 py-3 w-36">
                    <ScoreBar value={r.bvi} />
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-700">{Math.round(r.total_points)}</td>
                  <td className="px-4 py-3 font-mono text-gray-700">{r.wins}</td>
                  <td className="px-4 py-3 font-mono text-gray-700">{r.podiums}</td>
                  <td className="px-4 py-3"><TierBadge tier={r.tier} /></td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{r.perf_score.toFixed(1)}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{r.cons_score.toFixed(1)}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{r.expo_score.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
