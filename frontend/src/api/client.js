import axios from "axios"

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

const api = axios.create({
  baseURL: `${BASE}/api/v1`,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
})

// ── BVI ───────────────────────────────────────────────────────────────────────

export const getBviScores = (season = 2023) =>
  api.get("/bvi/scores", { params: { season } }).then((r) => r.data)

export const getBviCompare = (constructorA, constructorB, season = 2023) =>
  api
    .get("/bvi/compare", {
      params: { constructor_a: constructorA, constructor_b: constructorB, season },
    })
    .then((r) => r.data)

// ── Constructors ──────────────────────────────────────────────────────────────

export const getConstructorRankings = (season = 2023) =>
  api.get("/constructors/rankings", { params: { season } }).then((r) => r.data)

// ── Drivers ───────────────────────────────────────────────────────────────────

export const getDriverAnalytics = (driverId, season = 2023) =>
  api
    .get(`/drivers/analytics/${driverId}`, { params: { season } })
    .then((r) => r.data)

// ── Seasons ───────────────────────────────────────────────────────────────────

export const getSeasonComparison = (constructor) =>
  api.get("/season/comparison", { params: { constructor } }).then((r) => r.data)

// ── Circuits ──────────────────────────────────────────────────────────────────

export const getCircuitPerformance = (circuitId) =>
  api.get(`/circuits/${circuitId}/performance`).then((r) => r.data)

// ── Predictions ───────────────────────────────────────────────────────────────

export const predictPodium = (payload) =>
  api.post("/predict/podium", payload).then((r) => r.data)

// ── Sponsorship ───────────────────────────────────────────────────────────────

export const getSponsorshipTiers = (season = 2023) =>
  api.get("/sponsorship/tiers", { params: { season } }).then((r) => r.data)
