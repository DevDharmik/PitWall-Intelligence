import {
  RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip,
} from "recharts"

export default function BviRadarChart({ perf, cons, expo, name }) {
  const data = [
    { dim: "Performance", value: perf },
    { dim: "Consistency", value: cons },
    { dim: "Exposure",    value: expo },
  ]

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <PolarGrid stroke="#e5e7eb" />
        <PolarAngleAxis
          dataKey="dim"
          tick={{ fontSize: 12, fill: "#6b7280", fontFamily: "DM Mono" }}
        />
        <PolarRadiusAxis
          angle={30}
          domain={[0, 100]}
          tick={{ fontSize: 10, fill: "#9ca3af" }}
        />
        <Radar
          name={name || "BVI"}
          dataKey="value"
          stroke="#C8102E"
          fill="#C8102E"
          fillOpacity={0.15}
          strokeWidth={2}
        />
        <Tooltip
          formatter={(v) => [`${v.toFixed(1)}`, "Score"]}
          contentStyle={{
            fontSize: 12,
            fontFamily: "DM Mono",
            borderRadius: 6,
            border: "1px solid #e5e7eb",
          }}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
