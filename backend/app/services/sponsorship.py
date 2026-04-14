"""
app/services/sponsorship.py
────────────────────────────
Sponsorship tier classification logic.
Wraps BVI scores into Tier 1 / Tier 2 / Tier 3 groups
with labels and thresholds for the frontend tier grid.
"""

from app.models.schemas import BviScoreOut, TierGroupOut, SponsorshipTiersResponse


TIER_CONFIG = {
    1: {"label": "Tier 1 — Premium",  "threshold": "BVI >= 75"},
    2: {"label": "Tier 2 — Growth",   "threshold": "BVI 50–75"},
    3: {"label": "Tier 3 — Value",    "threshold": "BVI < 50"},
}


def classify_tiers(
    season: int,
    scores: list[BviScoreOut],
) -> SponsorshipTiersResponse:
    """
    Group a list of BVI scores into sponsorship tiers.
    Returns a SponsorshipTiersResponse ready for the API.
    """
    groups: dict[int, list[BviScoreOut]] = {1: [], 2: [], 3: []}

    for score in scores:
        groups[score.tier].append(score)

    tiers = [
        TierGroupOut(
            tier=tier,
            label=TIER_CONFIG[tier]["label"],
            threshold=TIER_CONFIG[tier]["threshold"],
            constructors=sorted(
                groups[tier], key=lambda x: x.bvi, reverse=True
            ),
        )
        for tier in [1, 2, 3]
    ]

    return SponsorshipTiersResponse(season=season, tiers=tiers)


def tier_label(bvi: float) -> str:
    """Return the tier label string for a given BVI score."""
    if bvi >= 75:
        return "Tier 1 — Premium"
    elif bvi >= 50:
        return "Tier 2 — Growth"
    return "Tier 3 — Value"


def tier_number(bvi: float) -> int:
    """Return tier number (1/2/3) for a given BVI score."""
    if bvi >= 75:
        return 1
    elif bvi >= 50:
        return 2
    return 3
