"""
app/models/schemas.py
─────────────────────
Pydantic v2 request/response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── BVI ───────────────────────────────────────────────────────────────────────

class BviScoreOut(BaseModel):
    constructor_id:  int
    constructor:     str
    season:          int
    total_points:    float
    wins:            int
    podiums:         int
    entries:         int
    dnf_rate:        float
    pts_finish_rate: float
    perf_score:      float
    cons_score:      float
    expo_score:      float
    bvi:             float
    tier:            int

    model_config = {"from_attributes": True}


class BviScoresResponse(BaseModel):
    season:  int
    count:   int
    results: list[BviScoreOut]


class BviCompareResponse(BaseModel):
    season:        int
    constructor_a: BviScoreOut
    constructor_b: BviScoreOut


# ── Constructors ──────────────────────────────────────────────────────────────

class ConstructorRankingOut(BaseModel):
    constructor_id:   int
    constructor:      str
    season:           int
    total_points:     float
    wins:             int
    podiums:          int
    bvi:              float
    tier:             int
    perf_score:       float
    cons_score:       float
    expo_score:       float
    championship_pos: int

    model_config = {"from_attributes": True}


class ConstructorRankingsResponse(BaseModel):
    season:  int
    results: list[ConstructorRankingOut]


# ── Drivers ───────────────────────────────────────────────────────────────────

class DriverAnalyticsOut(BaseModel):
    driver_id:        int
    forename:         str
    surname:          str
    nationality:      Optional[str]
    constructor:      str
    season:           int
    total_points:     float
    wins:             int
    podiums:          int
    dnf_count:        int
    avg_grid:         float
    avg_finish:       float
    avg_position_gain: float

    model_config = {"from_attributes": True}


# ── Seasons ───────────────────────────────────────────────────────────────────

class SeasonTrendPoint(BaseModel):
    season:      int
    bvi:         float
    perf_score:  float
    cons_score:  float
    expo_score:  float
    total_points: float
    wins:        int


class SeasonComparisonResponse(BaseModel):
    constructor: str
    trends:      list[SeasonTrendPoint]


# ── Circuits ──────────────────────────────────────────────────────────────────

class CircuitPerformanceOut(BaseModel):
    circuit_id:   int
    circuit_name: str
    country:      str
    constructor:  str
    races:        int
    wins:         int
    podiums:      int
    win_rate:     float
    avg_finish:   float

    model_config = {"from_attributes": True}


# ── Predictions ───────────────────────────────────────────────────────────────

class PodiumPredictRequest(BaseModel):
    constructor_id: int     = Field(..., description="Constructor ID")
    circuit_id:     int     = Field(..., description="Circuit ID")
    grid_position:  int     = Field(..., ge=1, le=20, description="Starting grid position")
    is_wet:         bool    = Field(False, description="Wet race conditions")
    season:         int     = Field(..., ge=2018, le=2030, description="Season year")


class PodiumPredictResponse(BaseModel):
    constructor_id:      int
    circuit_id:          int
    grid_position:       int
    podium_probability:  float = Field(..., description="Probability 0.0–1.0")
    confidence_interval: list[float] = Field(..., description="[lower, upper] 95% CI")
    prediction:          str  = Field(..., description="'podium' or 'no podium'")


# ── Sponsorship tiers ─────────────────────────────────────────────────────────

class TierGroupOut(BaseModel):
    tier:         int
    label:        str
    threshold:    str
    constructors: list[BviScoreOut]


class SponsorshipTiersResponse(BaseModel):
    season: int
    tiers:  list[TierGroupOut]


# ── Admin ─────────────────────────────────────────────────────────────────────

class RetrainResponse(BaseModel):
    status:  str
    message: str
