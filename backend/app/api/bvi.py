"""
app/api/bvi.py
──────────────
BVI endpoints:
  GET /api/v1/bvi/scores   — all constructor BVI scores for a season
  GET /api/v1/bvi/compare  — side-by-side comparison of two constructors
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.cache import cache_get, cache_set, bvi_scores_key, bvi_compare_key
from app.services.bvi_engine import get_bvi_scores, get_bvi_for_constructor
from app.models.schemas import BviScoresResponse, BviCompareResponse

router = APIRouter()


@router.get("/bvi/scores", response_model=BviScoresResponse)
async def bvi_scores(
    season: int = Query(2023, ge=2018, le=2030, description="F1 season year"),
    db: AsyncSession = Depends(get_db),
):
    """
    Return BVI scores for all constructors in a given season,
    sorted by composite BVI descending.
    Results are cached for 24 hours in Redis.
    """
    cache_key = bvi_scores_key(season)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    scores = await get_bvi_scores(season, db)
    if not scores:
        raise HTTPException(
            status_code=404,
            detail=f"No BVI data found for season {season}. "
                   "Run 'make seed' to load data.",
        )

    response = BviScoresResponse(
        season=season,
        count=len(scores),
        results=scores,
    )
    await cache_set(cache_key, response.model_dump())
    return response


@router.get("/bvi/compare", response_model=BviCompareResponse)
async def bvi_compare(
    constructor_a: str = Query(..., description="First constructor name"),
    constructor_b: str = Query(..., description="Second constructor name"),
    season: int = Query(2023, ge=2018, le=2030, description="F1 season year"),
    db: AsyncSession = Depends(get_db),
):
    """
    Return a side-by-side BVI comparison for two constructors in a season.
    """
    cache_key = bvi_compare_key(constructor_a, constructor_b, season)
    cached = await cache_get(cache_key)
    if cached:
        return cached

    score_a = await get_bvi_for_constructor(constructor_a, season, db)
    score_b = await get_bvi_for_constructor(constructor_b, season, db)

    if not score_a:
        raise HTTPException(
            status_code=404,
            detail=f"Constructor '{constructor_a}' not found for season {season}.",
        )
    if not score_b:
        raise HTTPException(
            status_code=404,
            detail=f"Constructor '{constructor_b}' not found for season {season}.",
        )

    response = BviCompareResponse(
        season=season,
        constructor_a=score_a,
        constructor_b=score_b,
    )
    await cache_set(cache_key, response.model_dump())
    return response
