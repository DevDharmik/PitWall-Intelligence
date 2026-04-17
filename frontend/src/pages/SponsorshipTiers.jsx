import { useState, useEffect } from "react"
import { getSponsorshipTiers } from "../api/client"
import ScoreBar from "../components/ScoreBar"

const SEASONS = [2018, 2019, 2020, 2021, 2022, 2023]

const TIER_STYLES = {
  1: { heading: "text-green-800", border: "border-green-200", bg: "bg-green-50",  dot: "bg-green-500" },
  2: { heading: "text-orange-800",border: "border-orange-200",bg: "bg-orange-50", dot: "bg-orange-500" },
  3: { heading: "text-red-800",   border: "border-red-200",  bg: "bg-red-50",    dot: "bg-red-400" },
}

export default function SponsorshipTiers() {
  const [season, setSeason]   = useState(2023)
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    getSponsorshipTiers(season)
      .then(setData)
      .catch(() => setError("Failed to load sponsorship tiers."))
      .finally(() => setLoading(false))
  }, [season])

  const downloadCsv = () => {
    if (!data) return
    const rows = [["Constructor", "BVI", "Tier", "Points", "Wins", "Podiums"]]
    data.tiers.forEach((t) =>
      t.constructors.forEach((c) =>
        rows.push([c.constructor, c.bvi, t.tier, c.total_points, c.wins, c.podiums])
      )
    )
    const csv  = rows.map((r) => r.join(",")).join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement("a")
    a.href     = url
    a.download = `pitwall_tiers_${season}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Sponsorship Tiers</h1>
          <p className="text-sm text-gray-500 mt-1">
            Tier 1 (BVI ≥ 75) · Tier 2 (50–75) · Tier 3 (&lt; 50)
          </p>
        </div>
        {data && (
          <button
            onClick={downloadCsv}
            className="text-xs font-mono border border-gray-200 px-3 py-1.5 rounded-lg text-gray-500 hover:border-gray-400 transition-colors"
          >
            Export CSV
          </button>
        )}
      </div>

      {/* Season selector */}
      <div className="flex gap-2 mb-6">
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

      {loading && <div className="text-center py-20 text-gray-400 text-sm">Loading…</div>}
      {error   && <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {data.tiers.map((tier) => {
            const s = TIER_STYLES[tier.tier]
            return (
              <div key={tier.tier} className={`rounded-xl border ${s.border} overflow-hidden`}>

                {/* Tier header */}
                <div className={`px-4 py-3 ${s.bg} border-b ${s.border}`}>
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${s.dot}`} />
                    <span className={`text-xs font-mono font-semibold uppercase tracking-wider ${s.heading}`}>
                      {tier.label}
                    </span>
                  </div>
                  <p className="text-xs font-mono text-gray-400 mt-0.5">{tier.threshold}</p>
                </div>

                {/* Constructor cards */}
                <div className="divide-y divide-gray-100 bg-white">
                  {tier.constructors.length === 0 && (
                    <p className="px-4 py-6 text-xs text-gray-400 text-center">
                      No constructors in this tier
                    </p>
                  )}
                  {tier.constructors.map((c) => (
                    <div key={c.constructor_id} className="px-4 py-3">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-sm font-medium text-gray-900">{c.constructor}</span>
                        <span className="text-sm font-mono font-semibold text-gray-700">
                          {c.bvi.toFixed(1)}
                        </span>
                      </div>
                      <ScoreBar value={c.bvi} />
                      <div className="flex gap-3 mt-2 text-xs font-mono text-gray-400">
                        <span>{Math.round(c.total_points)} pts</span>
                        <span>{c.wins}W</span>
                        <span>{c.podiums}P</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
