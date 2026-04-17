import { Routes, Route, Navigate } from "react-router-dom"
import Navbar from "./components/Navbar"
import BviOverview from "./pages/BviOverview"
import ConstructorRankings from "./pages/ConstructorRankings"
import DriverAnalytics from "./pages/DriverAnalytics"
import SeasonComparison from "./pages/SeasonComparison"
import CircuitIntelligence from "./pages/CircuitIntelligence"
import PodiumPredictor from "./pages/PodiumPredictor"
import SponsorshipTiers from "./pages/SponsorshipTiers"

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/"                   element={<Navigate to="/overview" replace />} />
          <Route path="/overview"           element={<BviOverview />} />
          <Route path="/rankings"           element={<ConstructorRankings />} />
          <Route path="/drivers"            element={<DriverAnalytics />} />
          <Route path="/seasons"            element={<SeasonComparison />} />
          <Route path="/circuits"           element={<CircuitIntelligence />} />
          <Route path="/predictor"          element={<PodiumPredictor />} />
          <Route path="/tiers"              element={<SponsorshipTiers />} />
          <Route path="*"                   element={<Navigate to="/overview" replace />} />
        </Routes>
      </main>
    </div>
  )
}
