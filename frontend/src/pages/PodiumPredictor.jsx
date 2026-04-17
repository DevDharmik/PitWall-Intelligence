import { useState } from "react"
import { predictPodium } from "../api/client"

const CONSTRUCTORS = [
  { id: 131, name: "Red Bull" },
  { id: 1,   name: "McLaren" },
  { id: 6,   name: "Ferrari" },
  { id: 1,   name: "Mercedes" },
  { id: 117, name: "Aston Martin" },
  { id: 214, name: "Alpine" },
  { id: 210, name: "Williams" },
  { id: 213, name: "Haas" },
]

const CIRCUITS = [
  { id: 6,  name: "Monaco" },
  { id: 9,  name: "Silverstone" },
  { id: 13, name: "Spa" },
  { id: 10, name: "Monza" },
  { id: 24, name: "Bahrain" },
  { id: 70, name: "Zandvoort" },
  { id: 73, name: "Jeddah" },
]

export default function PodiumPredictor() {
  const [form, setForm] = useState({
    constructor_id: 131,
    circuit_id:     6,
    grid_position:  1,
    is_wet:         false,
    season:         2023,
  })
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const set = (k, v) => setForm((prev) => ({ ...prev, [k]: v }))

  const submit = () => {
    setLoading(true)
    setError(null)
    setResult(null)
    predictPodium(form)
      .then(setResult)
      .catch(() => setError("Prediction failed. Is the backend running?"))
      .finally(() => setLoading(false))
  }

  const probPct = result ? Math.round(result.podium_probability * 100) : 0
  const isPodium = result?.prediction === "podium"

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Podium Predictor</h1>
        <p className="text-sm text-gray-500 mt-1">
          Logistic regression classifier — podium probability given race conditions
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Input form */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-5">
          <p className="text-xs font-mono text-gray-400 uppercase tracking-wider">Race conditions</p>

          <div>
            <label className="block text-xs font-mono text-gray-500 mb-2">Constructor</label>
            <select
              value={form.constructor_id}
              onChange={(e) => set("constructor_id", Number(e.target.value))}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700"
            >
              {CONSTRUCTORS.map((c) => (
                <option key={`${c.id}-${c.name}`} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-mono text-gray-500 mb-2">Circuit</label>
            <select
              value={form.circuit_id}
              onChange={(e) => set("circuit_id", Number(e.target.value))}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700"
            >
              {CIRCUITS.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-mono text-gray-500 mb-2">
              Grid position: <span className="text-f1red font-semibold">P{form.grid_position}</span>
            </label>
            <input
              type="range"
              min={1} max={20} step={1}
              value={form.grid_position}
              onChange={(e) => set("grid_position", Number(e.target.value))}
              className="w-full accent-f1red"
            />
            <div className="flex justify-between text-xs font-mono text-gray-300 mt-1">
              <span>P1</span><span>P20</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-gray-500 mb-2">Season</label>
            <div className="flex gap-2">
              {[2021, 2022, 2023].map((yr) => (
                <button
                  key={yr}
                  onClick={() => set("season", yr)}
                  className={`px-3 py-1 rounded text-sm font-mono border transition-colors ${
                    form.season === yr
                      ? "bg-f1red text-white border-f1red"
                      : "border-gray-200 text-gray-500 hover:border-gray-400"
                  }`}
                >
                  {yr}
                </button>
              ))}
            </div>
          </div>

          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_wet}
              onChange={(e) => set("is_wet", e.target.checked)}
              className="w-4 h-4 accent-f1red"
            />
            <span className="text-sm text-gray-700">Wet race conditions</span>
          </label>

          <button
            onClick={submit}
            disabled={loading}
            className="w-full bg-f1red text-white rounded-lg px-4 py-3 text-sm font-semibold hover:bg-f1red-dark transition-colors disabled:opacity-50"
          >
            {loading ? "Computing…" : "Predict podium probability"}
          </button>
        </div>

        {/* Result panel */}
        <div className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>
          )}

          {result && (
            <>
              {/* Probability gauge */}
              <div className={`rounded-xl p-6 border ${
                isPodium
                  ? "bg-green-50 border-green-200"
                  : "bg-gray-50 border-gray-200"
              }`}>
                <p className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
                  Prediction
                </p>
                <div className="flex items-end gap-3 mb-4">
                  <span className={`text-5xl font-mono font-bold ${
                    isPodium ? "text-green-700" : "text-gray-500"
                  }`}>
                    {probPct}%
                  </span>
                  <span className={`text-sm font-semibold mb-2 ${
                    isPodium ? "text-green-700" : "text-gray-500"
                  }`}>
                    podium probability
                  </span>
                </div>

                {/* Progress bar */}
                <div className="h-3 bg-white rounded-full overflow-hidden border border-gray-200 mb-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-700 ${
                      isPodium ? "bg-green-500" : "bg-gray-400"
                    }`}
                    style={{ width: `${probPct}%` }}
                  />
                </div>

                <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                  isPodium
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-200 text-gray-600"
                }`}>
                  {isPodium ? "Podium likely" : "No podium expected"}
                </div>
              </div>

              {/* Confidence interval */}
              <div className="bg-white border border-gray-200 rounded-xl p-5">
                <p className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
                  95% confidence interval
                </p>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-mono text-gray-600">
                    {Math.round(result.confidence_interval[0] * 100)}%
                  </span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full relative">
                    <div
                      className="absolute h-2 bg-blue-200 rounded-full"
                      style={{
                        left:  `${result.confidence_interval[0] * 100}%`,
                        width: `${(result.confidence_interval[1] - result.confidence_interval[0]) * 100}%`,
                      }}
                    />
                    <div
                      className="absolute w-2 h-2 bg-f1red rounded-full -translate-y-0"
                      style={{ left: `calc(${probPct}% - 4px)` }}
                    />
                  </div>
                  <span className="text-sm font-mono text-gray-600">
                    {Math.round(result.confidence_interval[1] * 100)}%
                  </span>
                </div>
              </div>

              {/* Input summary */}
              <div className="bg-white border border-gray-200 rounded-xl p-5">
                <p className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-3">
                  Input summary
                </p>
                <div className="grid grid-cols-2 gap-3 text-sm font-mono">
                  <div><span className="text-gray-400">Grid:</span> <span className="text-gray-800">P{result.grid_position}</span></div>
                  <div><span className="text-gray-400">Season:</span> <span className="text-gray-800">{form.season}</span></div>
                  <div><span className="text-gray-400">Wet:</span> <span className="text-gray-800">{form.is_wet ? "Yes" : "No"}</span></div>
                </div>
              </div>
            </>
          )}

          {!result && !loading && !error && (
            <div className="text-center py-20 text-gray-400 text-sm">
              Configure race conditions and click Predict.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
