"""
app/services/bvi_engine.py
──────────────────────────
BVI scoring engine — queries bvi_scores table and assembles
response objects. Also exposes the raw computation logic so
the admin retrain endpoint can recompute scores on-demand.
"""

import logging
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import BviScore, Constructor
from app.models.schemas import BviScoreOut

log = logging.getLogger(__name__)


# ── Fetch from DB ─────────────────────────────────────────────────────────────

async def get_bvi_scores(season: int, db: AsyncSession) -> list[BviScoreOut]:
    """Return all BVI scores for a given season, sorted by BVI desc."""
    stmt = (
        select(BviScore, Constructor.name.label("constructor_name"))
        .join(Constructor, BviScore.constructor_id == Constructor.constructor_id)
        .where(BviScore.season == season)
        .order_by(BviScore.bvi.desc())
    )
    rows = (await db.execute(stmt)).all()

    return [
        BviScoreOut(
            constructor_id=row.BviScore.constructor_id,
            constructor=row.constructor_name,
            season=row.BviScore.season,
            total_points=float(row.BviScore.total_points or 0),
            wins=row.BviScore.wins or 0,
            podiums=row.BviScore.podiums or 0,
            entries=row.BviScore.entries or 0,
            dnf_rate=float(row.BviScore.dnf_rate or 0),
            pts_finish_rate=float(row.BviScore.pts_finish_rate or 0),
            perf_score=float(row.BviScore.perf_score or 0),
            cons_score=float(row.BviScore.cons_score or 0),
            expo_score=float(row.BviScore.expo_score or 0),
            bvi=float(row.BviScore.bvi or 0),
            tier=row.BviScore.tier or 3,
        )
        for row in rows
    ]


async def get_bvi_for_constructor(
    constructor_name: str, season: int, db: AsyncSession
) -> BviScoreOut | None:
    """Return BVI score for a single constructor in a given season."""
    stmt = (
        select(BviScore, Constructor.name.label("constructor_name"))
        .join(Constructor, BviScore.constructor_id == Constructor.constructor_id)
        .where(BviScore.season == season)
        .where(Constructor.name.ilike(f"%{constructor_name}%"))
    )
    row = (await db.execute(stmt)).first()
    if not row:
        return None

    return BviScoreOut(
        constructor_id=row.BviScore.constructor_id,
        constructor=row.constructor_name,
        season=row.BviScore.season,
        total_points=float(row.BviScore.total_points or 0),
        wins=row.BviScore.wins or 0,
        podiums=row.BviScore.podiums or 0,
        entries=row.BviScore.entries or 0,
        dnf_rate=float(row.BviScore.dnf_rate or 0),
        pts_finish_rate=float(row.BviScore.pts_finish_rate or 0),
        perf_score=float(row.BviScore.perf_score or 0),
        cons_score=float(row.BviScore.cons_score or 0),
        expo_score=float(row.BviScore.expo_score or 0),
        bvi=float(row.BviScore.bvi or 0),
        tier=row.BviScore.tier or 3,
    )


async def get_season_trends(
    constructor_name: str, db: AsyncSession
) -> list[BviScoreOut]:
    """Return BVI scores across all seasons for a given constructor."""
    stmt = (
        select(BviScore, Constructor.name.label("constructor_name"))
        .join(Constructor, BviScore.constructor_id == Constructor.constructor_id)
        .where(Constructor.name.ilike(f"%{constructor_name}%"))
        .order_by(BviScore.season.asc())
    )
    rows = (await db.execute(stmt)).all()

    return [
        BviScoreOut(
            constructor_id=row.BviScore.constructor_id,
            constructor=row.constructor_name,
            season=row.BviScore.season,
            total_points=float(row.BviScore.total_points or 0),
            wins=row.BviScore.wins or 0,
            podiums=row.BviScore.podiums or 0,
            entries=row.BviScore.entries or 0,
            dnf_rate=float(row.BviScore.dnf_rate or 0),
            pts_finish_rate=float(row.BviScore.pts_finish_rate or 0),
            perf_score=float(row.BviScore.perf_score or 0),
            cons_score=float(row.BviScore.cons_score or 0),
            expo_score=float(row.BviScore.expo_score or 0),
            bvi=float(row.BviScore.bvi or 0),
            tier=row.BviScore.tier or 3,
        )
        for row in rows
    ]
