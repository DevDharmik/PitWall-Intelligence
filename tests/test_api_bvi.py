"""
tests/test_api_bvi.py
──────────────────────
Integration tests for the BVI API endpoints.
Uses httpx AsyncClient against the FastAPI app.
Requires a running PostgreSQL + Redis (use docker compose run --rm backend pytest).
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app

BASE = "/api/v1"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# ── Health check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── GET /api/v1/bvi/scores ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_bvi_scores_default_season(client):
    r = await client.get(f"{BASE}/bvi/scores")
    assert r.status_code in (200, 404)  # 404 if DB not seeded
    if r.status_code == 200:
        data = r.json()
        assert "season" in data
        assert "results" in data
        assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_bvi_scores_valid_season(client):
    r = await client.get(f"{BASE}/bvi/scores", params={"season": 2023})
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert data["season"] == 2023
        assert data["count"] == len(data["results"])


@pytest.mark.asyncio
async def test_bvi_scores_invalid_season_low(client):
    r = await client.get(f"{BASE}/bvi/scores", params={"season": 2010})
    assert r.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_bvi_scores_invalid_season_high(client):
    r = await client.get(f"{BASE}/bvi/scores", params={"season": 2099})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_bvi_scores_sorted_descending(client):
    r = await client.get(f"{BASE}/bvi/scores", params={"season": 2023})
    if r.status_code == 200:
        scores = [item["bvi"] for item in r.json()["results"]]
        assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_bvi_scores_schema(client):
    r = await client.get(f"{BASE}/bvi/scores", params={"season": 2023})
    if r.status_code == 200:
        item = r.json()["results"][0]
        required_fields = [
            "constructor_id", "constructor", "season",
            "total_points", "wins", "podiums",
            "perf_score", "cons_score", "expo_score",
            "bvi", "tier",
        ]
        for field in required_fields:
            assert field in item, f"Missing field: {field}"


# ── GET /api/v1/bvi/compare ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_bvi_compare_requires_params(client):
    r = await client.get(f"{BASE}/bvi/compare")
    assert r.status_code == 422  # missing required query params


@pytest.mark.asyncio
async def test_bvi_compare_valid(client):
    r = await client.get(
        f"{BASE}/bvi/compare",
        params={
            "constructor_a": "Red Bull",
            "constructor_b": "Mercedes",
            "season": 2023,
        }
    )
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert "constructor_a" in data
        assert "constructor_b" in data
        assert data["season"] == 2023


@pytest.mark.asyncio
async def test_bvi_compare_unknown_constructor(client):
    r = await client.get(
        f"{BASE}/bvi/compare",
        params={
            "constructor_a": "NonExistentTeamXYZ",
            "constructor_b": "Mercedes",
            "season": 2023,
        }
    )
    assert r.status_code in (404, 200)


# ── GET /api/v1/constructors/rankings ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_constructor_rankings(client):
    r = await client.get(f"{BASE}/constructors/rankings", params={"season": 2023})
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert "results" in data
        for item in data["results"]:
            assert "championship_pos" in item
            assert "bvi" in item


# ── GET /api/v1/sponsorship/tiers ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sponsorship_tiers(client):
    r = await client.get(f"{BASE}/sponsorship/tiers", params={"season": 2023})
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert "tiers" in data
        tier_numbers = [t["tier"] for t in data["tiers"]]
        assert sorted(tier_numbers) == [1, 2, 3]


# ── GET /api/v1/season/comparison ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_season_comparison(client):
    r = await client.get(
        f"{BASE}/season/comparison",
        params={"constructor": "Red Bull"}
    )
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert "trends" in data
        assert isinstance(data["trends"], list)
        for point in data["trends"]:
            assert "season" in point
            assert "bvi" in point
