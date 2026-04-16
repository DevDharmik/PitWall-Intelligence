"""
tests/test_predict.py
──────────────────────
Integration tests for the podium prediction endpoint
and the ML registry fallback behaviour.
"""

import pytest
import pytest_asyncio
import numpy as np
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.ml_registry import MlRegistry, _FallbackClassifier, _FallbackRegressor

BASE = "/api/v1"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# ── ML Registry unit tests ────────────────────────────────────────────────────

class TestMlRegistry:

    def test_registry_loads_without_model_files(self):
        """Registry should not raise even when joblib files are missing."""
        registry = MlRegistry()
        registry.load_all()  # Should use fallbacks silently
        assert registry._loaded is True

    def test_fallback_classifier_returns_valid_proba(self):
        clf = _FallbackClassifier()
        result = clf.predict_proba([[1, 0, 0.5, 5.0]])
        assert result.shape == (1, 2)
        assert abs(result[0].sum() - 1.0) < 1e-6
        assert 0.0 <= result[0][1] <= 1.0

    def test_fallback_regressor_returns_float(self):
        reg = _FallbackRegressor()
        result = reg.predict([[5.0, 0.9, 3.0, 0.8]])
        assert isinstance(float(result[0]), float)

    def test_predict_podium_probability_range(self):
        registry = MlRegistry()
        registry.load_all()
        prob, ci = registry.predict_podium_probability(
            grid_position=1,
            is_wet=False,
            circuit_win_rate=0.4,
            rolling_avg_finish=2.0,
        )
        assert 0.0 <= prob <= 1.0
        assert len(ci) == 2
        assert ci[0] <= prob <= ci[1]

    def test_predict_podium_pole_vs_backmarker(self):
        """Pole sitter should have higher probability than P20 starter."""
        registry = MlRegistry()
        registry.load_all()

        prob_pole, _ = registry.predict_podium_probability(
            grid_position=1, is_wet=False,
            circuit_win_rate=0.5, rolling_avg_finish=1.5,
        )
        prob_last, _ = registry.predict_podium_probability(
            grid_position=20, is_wet=False,
            circuit_win_rate=0.0, rolling_avg_finish=18.0,
        )
        assert prob_pole > prob_last

    def test_confidence_interval_valid(self):
        registry = MlRegistry()
        registry.load_all()
        _, ci = registry.predict_podium_probability(
            grid_position=5, is_wet=True,
            circuit_win_rate=0.2, rolling_avg_finish=4.0,
        )
        lower, upper = ci
        assert lower >= 0.0
        assert upper <= 1.0
        assert lower <= upper

    def test_predict_constructor_points_returns_float(self):
        registry = MlRegistry()
        registry.load_all()
        pts = registry.predict_constructor_points([3.0, 0.85, 2, 1.5])
        assert isinstance(pts, float)
        assert pts >= 0.0

    def test_reload_does_not_raise(self):
        registry = MlRegistry()
        registry.load_all()
        registry.reload()  # Should re-load without error
        assert registry._loaded is True


# ── POST /api/v1/predict/podium ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_podium_valid_request(client):
    payload = {
        "constructor_id": 131,   # Red Bull constructorId in Kaggle dataset
        "circuit_id": 6,          # Monaco
        "grid_position": 1,
        "is_wet": False,
        "season": 2023,
    }
    r = await client.post(f"{BASE}/predict/podium", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "podium_probability" in data
    assert "confidence_interval" in data
    assert "prediction" in data
    assert 0.0 <= data["podium_probability"] <= 1.0
    assert data["prediction"] in ("podium", "no podium")
    assert len(data["confidence_interval"]) == 2


@pytest.mark.asyncio
async def test_predict_podium_invalid_grid(client):
    payload = {
        "constructor_id": 131,
        "circuit_id": 6,
        "grid_position": 0,   # invalid — must be >= 1
        "is_wet": False,
        "season": 2023,
    }
    r = await client.post(f"{BASE}/predict/podium", json=payload)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_predict_podium_invalid_grid_too_high(client):
    payload = {
        "constructor_id": 131,
        "circuit_id": 6,
        "grid_position": 25,   # invalid — must be <= 20
        "is_wet": False,
        "season": 2023,
    }
    r = await client.post(f"{BASE}/predict/podium", json=payload)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_predict_podium_wet_race(client):
    payload = {
        "constructor_id": 131,
        "circuit_id": 6,
        "grid_position": 3,
        "is_wet": True,
        "season": 2023,
    }
    r = await client.post(f"{BASE}/predict/podium", json=payload)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_predict_podium_missing_fields(client):
    payload = {"constructor_id": 131}  # missing required fields
    r = await client.post(f"{BASE}/predict/podium", json=payload)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_predict_podium_invalid_season(client):
    payload = {
        "constructor_id": 131,
        "circuit_id": 6,
        "grid_position": 1,
        "is_wet": False,
        "season": 2010,   # below minimum (2018)
    }
    r = await client.post(f"{BASE}/predict/podium", json=payload)
    assert r.status_code == 422
