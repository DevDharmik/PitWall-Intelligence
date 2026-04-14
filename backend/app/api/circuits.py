"""
app/api/circuits.py
───────────────────
Circuit endpoints:
  GET /api/v1/circuits/{circuit_id}/performance — constructor stats at a circuit
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.orm import Circuit, Race, Result, Constructor
from app.models.schemas import CircuitPerformanceOut

router = APIRouter()


@router.get("/circuits/{circuit_id}/performance", response_model=list[CircuitPerformanceOut])
async def circuit_performance(
    circuit_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Return constructor performance statistics at a specific circuit,
    aggregated across all available seasons.
    Includes races, wins, podiums, win rate and average finishing position.
    """
    # Verify circuit exists
    circuit = await db.get(Circuit, circuit_id)
    if not circuit:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit {circuit_id} not found.",
        )

    # Aggregate results per constructor at this circuit
    stmt = (
        select(
            Constructor.constructor_id,
            Constructor.name.label("constructor_name"),
            func.count(Result.result_id).label("races"),
            func.sum(
                func.cast(Result.position_order == 1, Integer)
            ).label("wins"),
            func.sum(
                func.cast(Result.position_order <= 3, Integer)
            ).label("podiums"),
            func.avg(Result.position_order).label("avg_finish"),
        )
        .join(Race, Result.race_id == Race.race_id)
        .join(Constructor, Result.constructor_id == Constructor.constructor_id)
        .where(Race.circuit_id == circuit_id)
        .group_by(Constructor.constructor_id, Constructor.name)
        .order_by(func.count(Result.result_id).desc())
    )
    rows = (await db.execute(stmt)).all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for circuit {circuit_id}.",
        )

    return [
        CircuitPerformanceOut(
            circuit_id=circuit_id,
            circuit_name=circuit.name,
            country=circuit.country or "",
            constructor=row.constructor_name,
            races=row.races,
            wins=int(row.wins or 0),
            podiums=int(row.podiums or 0),
            win_rate=round(float(row.wins or 0) / row.races, 3),
            avg_finish=round(float(row.avg_finish or 0), 2),
        )
        for row in rows
    ]
