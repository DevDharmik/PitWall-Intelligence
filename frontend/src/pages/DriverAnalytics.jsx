import { useState } from "react"
import { getDriverAnalytics } from "../api/client"

const SEASONS = [2018, 2019, 2020, 2021, 2022, 2023]

// Common driver IDs from Kaggle dataset
const NOTABLE_DRIVERS = [
  { id: 1,   name: "Lewis Hamilton" },
  { id: 830, name: "Max Verstappen" },
  { id: 844, name: "Charles Leclerc" },
  { id: 832, name: "Carlos Sainz" },
  { id: 840, name: "Lando Norris" },
  { id: 842, name: "George Russell" },
  { id: 815, name: "Sebastian Vettel" },
  { id: 4,   name: "Fernando Alonso" },
  { id: 839, name: "Lance Stroll" },
  { id: 835, name: "Pierre Gasly" },
]

export default function DriverAnalytics() {
  const [driverId, setDriverId] = useState(830)
  const [season, setSeason]     = useState(2023)
  const [data, setData]         = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  const fetch = () => {
    setLoading(true)
    setError(null)
    setData(null)
    getDriverAnalytics(driverId, season)
      .then(setData)
      .catch(() => setError("Driver not found for this season."))
      .finally(() => setLoading(false))
  }

  const StatCard = ({ label, value }) => (
    <div className="bg-gray-50 rounded-lg p-4">
      <p className="text-xs font-mono text-gray-400 mb-1">{label}</p>
      <p className="text-xl font-mono font-semibold text-gray-900">{value}</p>
    </div>
  )

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Driver Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">
          Individual driver performance deep-dive
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-2">Driver</label>
            <select
              value={driverId}
              onChange={(e) => setDriverId(Number(e.target.value))}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700"
            >
              {NOTABLE_DRIVERS.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-2">Season</label>
            <div className="flex gap-2 flex-wrap">
              {SEASONS.map((yr) => (
                <button
                  key={yr}
                  onClick={() => setSeason(yr)}
                  className={`px-2.5 py-1 rounded text-xs font-mono border transition-colors ${
                    season === yr
                      ? "bg-f1red text-white border-f1red"
                      : "border-gray-200 text-gray-500 hover:border-gray-400"
                  }`}
                >
                  {yr}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-end">
            <button
              onClick={fetch}
              disabled={loading}
              className="w-full bg-f1red text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-f1red-dark transition-colors disabled:opacity-50"
            >
              {loading ? "Loading…" : "Analyse"}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>
      )}

      {data && (
        <div className="space-y-5">
          {/* Driver header */}
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {data.forename} {data.surname}
                </h2>
                <p className="text-sm text-gray-500">
                  {data.constructor} · {data.nationality} · {season}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-mono font-semibold text-f1red">
                  {Math.round(data.total_points)} pts
                </p>
              </div>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatCard label="Wins"            value={data.wins} />
            <StatCard label="Podiums"         value={data.podiums} />
            <StatCard label="DNFs"            value={data.dnf_count} />
            <StatCard label="Avg grid pos"    value={data.avg_grid.toFixed(1)} />
            <StatCard label="Avg finish pos"  value={data.avg_finish.toFixed(1)} />
            <StatCard label="Avg pos gained"  value={data.avg_position_gain.toFixed(1)} />
          </div>

          {/* Performance summary */}
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <p className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
              Performance summary
            </p>
            <div className="space-y-3">
              {[
                {
                  label: "Points finish rate",
                  value: data.total_points > 0 ? Math.min(100, data.total_points / 2) : 0,
                  suffix: "",
                },
                {
                  label: "Podium rate",
                  value: data.podiums > 0 ? (data.podiums / 22) * 100 : 0,
                  suffix: "",
                },
                {
                  label: "Avg positions gained",
                  value: Math.max(0, data.avg_position_gain * 5),
                  suffix: "",
                },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex justify-between text-xs font-mono text-gray-500 mb-1">
                    <span>{item.label}</span>
                    <span>{item.value.toFixed(1)}</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-1.5 bg-f1red rounded-full transition-all"
                      style={{ width: `${Math.min(100, item.value)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!data && !loading && !error && (
        <div className="text-center py-20 text-gray-400 text-sm">
          Select a driver and season, then click Analyse.
        </div>
      )}
    </div>
  )
}
