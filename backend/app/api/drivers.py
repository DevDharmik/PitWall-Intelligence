"""
app/api/drivers.py
──────────────────
Driver endpoints:
  GET /api/v1/drivers/analytics/{driver_id} — driver-level performance deep-dive
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.orm import Driver, Result, Race, Constructor
from app.models.schemas import DriverAnalyticsOut

router = APIRouter()

# DNF status IDs (approximate set — extend as needed)
DNF_STATUS_IDS = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                  18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29}


@router.get("/drivers/analytics/{driver_id}", response_model=DriverAnalyticsOut)
async def driver_analytics(
    driver_id: int,
    season: int = Query(2023, ge=2018, le=2030, description="F1 season year"),
    db: AsyncSession = Depends(get_db),
):
    """
    Return performance analytics for a single driver in a given season.
    Includes points, wins, podiums, DNFs, average grid/finish position,
    and average positions gained per race.
    """
    # Fetch driver
    driver = await db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found.")

    # Fetch results for this driver in this season
    stmt = (
        select(Result, Constructor.name.label("constructor_name"))
        .join(Race, Result.race_id == Race.race_id)
        .join(Constructor, Result.constructor_id == Constructor.constructor_id)
        .where(Result.driver_id == driver_id)
        .where(Race.season == season)
        .order_by(Race.round.asc())
    )
    rows = (await db.execute(stmt)).all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No results for driver {driver_id} in season {season}.",
        )

    results = [row.Result for row in rows]
    constructor_name = rows[0].constructor_name if rows else "Unknown"

    total_points = sum(float(r.points or 0) for r in results)
    wins         = sum(1 for r in results if r.position_order == 1)
    podiums      = sum(1 for r in results if (r.position_order or 99) <= 3)
    dnf_count    = sum(1 for r in results if r.status_id in DNF_STATUS_IDS)

    grids   = [r.grid for r in results if r.grid and r.grid > 0]
    finishes = [r.position_order for r in results if r.position_order]

    avg_grid   = round(sum(grids) / len(grids), 2) if grids else 0.0
    avg_finish = round(sum(finishes) / len(finishes), 2) if finishes else 0.0

    gains = [
        (r.grid - r.position_order)
        for r in results
        if r.grid and r.grid > 0 and r.position_order
    ]
    avg_gain = round(sum(gains) / len(gains), 2) if gains else 0.0

    return DriverAnalyticsOut(
        driver_id=driver_id,
        forename=driver.forename,
        surname=driver.surname,
        nationality=driver.nationality,
        constructor=constructor_name,
        season=season,
        total_points=total_points,
        wins=wins,
        podiums=podiums,
        dnf_count=dnf_count,
        avg_grid=avg_grid,
        avg_finish=avg_finish,
        avg_position_gain=avg_gain,
    )
