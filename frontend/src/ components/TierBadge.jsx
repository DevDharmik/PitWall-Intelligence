const CONFIG = {
  1: { label: "Tier 1", className: "bg-green-100 text-green-800" },
  2: { label: "Tier 2", className: "bg-orange-100 text-orange-800" },
  3: { label: "Tier 3", className: "bg-red-100 text-red-800" },
}

export default function TierBadge({ tier }) {
  const cfg = CONFIG[tier] || CONFIG[3]
  return (
    <span
      className={`inline-block text-xs font-mono px-2 py-0.5 rounded font-medium ${cfg.className}`}
    >
      {cfg.label}
    </span>
  )
}
