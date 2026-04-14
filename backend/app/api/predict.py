"""
app/api/predict.py
──────────────────
Prediction endpoints:
  POST /api/v1/predict/podium — podium probability for given race conditions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.orm import Result, Race, Constructor
from app.models.schemas import PodiumPredictRequest, PodiumPredictResponse
from app.services.ml_registry import ml_registry

router = APIRouter()


async def _get_circuit_win_rate(
    constructor_id: int, circuit_id: int, db: AsyncSession
) -> float:
    """Compute historical win rate for a constructor at a given circuit."""
    stmt = (
        select(
            func.count(Result.result_id).label("total"),
            func.sum(
                func.cast(Result.position_order == 1, Integer)
            ).label("wins"),
        )
        .join(Race, Result.race_id == Race.race_id)
        .where(Result.constructor_id == constructor_id)
        .where(Race.circuit_id == circuit_id)
    )
    row = (await db.execute(stmt)).first()
    if not row or not row.total:
        return 0.0
    return round(float(row.wins or 0) / row.total, 3)


async def _get_rolling_avg_finish(
    constructor_id: int, season: int, db: AsyncSession, last_n: int = 3
) -> float:
    """Compute rolling average finishing position over last N races."""
    stmt = (
        select(Result.position_order)
        .join(Race, Result.race_id == Race.race_id)
        .where(Result.constructor_id == constructor_id)
        .where(Race.season == season)
        .where(Result.position_order.isnot(None))
        .order_by(Race.round.desc())
        .limit(last_n * 2)  # 2 drivers per constructor
    )
    rows = (await db.execute(stmt)).scalars().all()
    if not rows:
        return 10.0  # default midfield
    return round(sum(rows) / len(rows), 2)


@router.post("/predict/podium", response_model=PodiumPredictResponse)
async def predict_podium(
    request: PodiumPredictRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Predict the probability of a constructor achieving a podium finish
    given race conditions (circuit, grid position, weather, season).

    Uses the logistic regression classifier trained in notebooks/04.
    Falls back to a rule-based estimate if the model is not loaded.
    """
    # Gather features
    circuit_win_rate = await _get_circuit_win_rate(
        request.constructor_id, request.circuit_id, db
    )
    rolling_avg_finish = await _get_rolling_avg_finish(
        request.constructor_id, request.season, db
    )

    probability, confidence_interval = ml_registry.predict_podium_probability(
        grid_position=request.grid_position,
        is_wet=request.is_wet,
        circuit_win_rate=circuit_win_rate,
        rolling_avg_finish=rolling_avg_finish,
    )

    return PodiumPredictResponse(
        constructor_id=request.constructor_id,
        circuit_id=request.circuit_id,
        grid_position=request.grid_position,
        podium_probability=probability,
        confidence_interval=confidence_interval,
        prediction="podium" if probability >= 0.5 else "no podium",
    )
