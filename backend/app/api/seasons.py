"""
app/api/seasons.py
──────────────────
Season endpoints:
  GET /api/v1/season/comparison — year-over-year BVI trend for a constructor
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.cache import cache_get, cache_set, season_comparison_key
from app.services.bvi_engine import get_season_trends
from app.models.schemas import SeasonComparisonResponse, SeasonTrendPoint

router = APIRouter()


@router.get("/season/comparison", response_model=SeasonComparisonResponse)
async def season_comparison(
    constructor: str = Query(..., description="Constructor name (partial match supported)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Return year-over-year BVI trend data for a given constructor
    across all available seasons (2018-2023).
    Useful for sponsors evaluating whether a team's value is improving
    or declining over time.
    """
    cache_key = season_comparison_key(constructor)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    scores = await get_season_trends(constructor, db)
    if not scores:
        raise HTTPException(
            status_code=404,
            detail=f"No season data found for constructor '{constructor}'.",
        )

    trends = [
        SeasonTrendPoint(
            season=s.season,
            bvi=s.bvi,
            perf_score=s.perf_score,
            cons_score=s.cons_score,
            expo_score=s.expo_score,
            total_points=s.total_points,
            wins=s.wins,
        )
        for s in scores
    ]

    response = SeasonComparisonResponse(
        constructor=scores[0].constructor,
        trends=trends,
    )
    await cache_set(cache_key, response.model_dump())
    return response
