import { NavLink } from "react-router-dom"

const LINKS = [
  { to: "/overview",  label: "BVI Overview" },
  { to: "/rankings",  label: "Rankings" },
  { to: "/drivers",   label: "Drivers" },
  { to: "/seasons",   label: "Season Trends" },
  { to: "/circuits",  label: "Circuits" },
  { to: "/predictor", label: "Podium Predictor" },
  { to: "/tiers",     label: "Sponsor Tiers" },
]

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center gap-8 h-14">

          {/* Logo */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="w-7 h-7 bg-f1red rounded flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-white">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="font-semibold text-sm text-gray-900 tracking-tight">
              PitWall
            </span>
          </div>

          {/* Nav links */}
          <div className="flex items-center gap-1 overflow-x-auto">
            {LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  [
                    "px-3 py-1.5 rounded text-sm whitespace-nowrap transition-colors",
                    isActive
                      ? "bg-f1red text-white font-medium"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-100",
                  ].join(" ")
                }
              >
                {link.label}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
