"""
app/api/constructors.py
───────────────────────
Constructor endpoints:
  GET /api/v1/constructors/rankings — championship standings + BVI metrics
  GET /api/v1/sponsorship/tiers     — tier 1/2/3 classification grid
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.cache import (
    cache_get, cache_set,
    constructor_rankings_key, sponsorship_tiers_key,
)
from app.services.bvi_engine import get_bvi_scores
from app.services.sponsorship import classify_tiers
from app.models.schemas import ConstructorRankingsResponse, ConstructorRankingOut, SponsorshipTiersResponse

router = APIRouter()


@router.get("/constructors/rankings", response_model=ConstructorRankingsResponse)
async def constructor_rankings(
    season: int = Query(2023, ge=2018, le=2030, description="F1 season year"),
    db: AsyncSession = Depends(get_db),
):
    """
    Return all constructors ranked by BVI for a season.
    Includes championship position, points, wins, and all BVI dimension scores.
    """
    cache_key = constructor_rankings_key(season)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    scores = await get_bvi_scores(season, db)
    if not scores:
        raise HTTPException(
            status_code=404,
            detail=f"No constructor data for season {season}.",
        )

    rankings = [
        ConstructorRankingOut(
            constructor_id=s.constructor_id,
            constructor=s.constructor,
            season=s.season,
            total_points=s.total_points,
            wins=s.wins,
            podiums=s.podiums,
            bvi=s.bvi,
            tier=s.tier,
            perf_score=s.perf_score,
            cons_score=s.cons_score,
            expo_score=s.expo_score,
            championship_pos=i + 1,
        )
        for i, s in enumerate(
            sorted(scores, key=lambda x: x.total_points, reverse=True)
        )
    ]

    response = ConstructorRankingsResponse(season=season, results=rankings)
    await cache_set(cache_key, response.model_dump())
    return response


@router.get("/sponsorship/tiers", response_model=SponsorshipTiersResponse)
async def sponsorship_tiers(
    season: int = Query(2023, ge=2018, le=2030, description="F1 season year"),
    db: AsyncSession = Depends(get_db),
):
    """
    Return all constructors classified into Tier 1 / 2 / 3 by BVI.
    Tier 1 = BVI >= 75 (Premium), Tier 2 = 50-75 (Growth), Tier 3 = <50 (Value).
    """
    cache_key = sponsorship_tiers_key(season)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    scores = await get_bvi_scores(season, db)
    if not scores:
        raise HTTPException(
            status_code=404,
            detail=f"No BVI data for season {season}.",
        )

    response = classify_tiers(season, scores)
    await cache_set(cache_key, response.model_dump())
    return response
