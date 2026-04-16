"""
tests/test_bvi_engine.py
─────────────────────────
Unit tests for the BVI scoring formula.
Tests the core maths — no database required.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Allow imports from etl/ without installing as a package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from etl.transform import minmax, compute_bvi


# ── minmax helper ─────────────────────────────────────────────────────────────

class TestMinmax:

    def test_basic_normalisation(self):
        s = pd.Series([0.0, 50.0, 100.0])
        result = minmax(s)
        assert result.tolist() == [0.0, 0.5, 1.0]

    def test_constant_series_returns_half(self):
        s = pd.Series([42.0, 42.0, 42.0])
        result = minmax(s)
        assert all(result == 0.5)

    def test_single_element(self):
        s = pd.Series([7.0])
        result = minmax(s)
        assert result.iloc[0] == 0.5

    def test_output_range(self):
        s = pd.Series(np.random.rand(100) * 1000)
        result = minmax(s)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_preserves_index(self):
        s = pd.Series([10.0, 20.0, 30.0], index=[5, 6, 7])
        result = minmax(s)
        assert list(result.index) == [5, 6, 7]


# ── BVI formula ───────────────────────────────────────────────────────────────

class TestBviFormula:

    def _make_results(self, n_constructors=3, season=2023):
        """Create a minimal fake results DataFrame for testing."""
        rows = []
        constructor_ids = list(range(1, n_constructors + 1))
        for cid in constructor_ids:
            for race in range(1, 11):
                rows.append({
                    "raceId": race,
                    "constructorId": cid,
                    "positionOrder": cid,       # constructor 1 always wins
                    "points": max(0, 25 - (cid - 1) * 8),
                    "grid": cid,
                    "statusId": 1,              # finished
                })
        return pd.DataFrame(rows)

    def _make_races(self, season=2023):
        return pd.DataFrame({
            "raceId": list(range(1, 11)),
            "year": [season] * 10,
        })

    def _make_status(self):
        return pd.DataFrame({
            "statusId": [1, 3],
            "status": ["Finished", "Engine"],
        })

    def _make_constructors(self, n=3):
        return pd.DataFrame({
            "constructorId": list(range(1, n + 1)),
            "name": [f"Team {i}" for i in range(1, n + 1)],
        })

    def test_bvi_output_shape(self):
        results      = self._make_results()
        races        = self._make_races()
        status       = self._make_status()
        constructors = self._make_constructors()

        bvi = compute_bvi(results, races, status, constructors)
        assert len(bvi) == 3  # 3 constructors, 1 season

    def test_bvi_range(self):
        results      = self._make_results()
        races        = self._make_races()
        status       = self._make_status()
        constructors = self._make_constructors()

        bvi = compute_bvi(results, races, status, constructors)
        assert (bvi["bvi"] >= 0).all()
        assert (bvi["bvi"] <= 100).all()

    def test_top_constructor_has_highest_bvi(self):
        results      = self._make_results()
        races        = self._make_races()
        status       = self._make_status()
        constructors = self._make_constructors()

        bvi = compute_bvi(results, races, status, constructors)
        top = bvi.sort_values("bvi", ascending=False).iloc[0]
        assert top["constructor_id"] == 1  # Team 1 always wins

    def test_tier_classification(self):
        results      = self._make_results()
        races        = self._make_races()
        status       = self._make_status()
        constructors = self._make_constructors()

        bvi = compute_bvi(results, races, status, constructors)
        assert set(bvi["tier"]).issubset({1, 2, 3})

    def test_tier_thresholds(self):
        """Tier 1 >= 75, Tier 2 50-75, Tier 3 < 50."""
        rows = [
            {"bvi": 80.0, "expected_tier": 1},
            {"bvi": 60.0, "expected_tier": 2},
            {"bvi": 30.0, "expected_tier": 3},
            {"bvi": 75.0, "expected_tier": 1},
            {"bvi": 50.0, "expected_tier": 2},
            {"bvi": 49.9, "expected_tier": 3},
        ]
        for r in rows:
            tier = 1 if r["bvi"] >= 75 else (2 if r["bvi"] >= 50 else 3)
            assert tier == r["expected_tier"], f"BVI={r['bvi']} → Tier {tier} (expected {r['expected_tier']})"

    def test_dnf_penalises_consistency(self):
        """Constructor with high DNF rate should have lower cons_score."""
        # Constructor 1: zero DNFs
        # Constructor 2: high DNFs (statusId=3 = Engine failure)
        rows = []
        for race in range(1, 11):
            rows.append({
                "raceId": race, "constructorId": 1,
                "positionOrder": 1, "points": 25,
                "grid": 1, "statusId": 1,
            })
            rows.append({
                "raceId": race, "constructorId": 2,
                "positionOrder": 15, "points": 0,
                "grid": 5, "statusId": 3,  # Engine DNF
            })

        results      = pd.DataFrame(rows)
        races        = self._make_races()
        status       = self._make_status()
        constructors = pd.DataFrame({
            "constructorId": [1, 2],
            "name": ["Reliable Team", "Unreliable Team"],
        })

        bvi = compute_bvi(results, races, status, constructors)
        reliable   = bvi[bvi["constructor_id"] == 1].iloc[0]
        unreliable = bvi[bvi["constructor_id"] == 2].iloc[0]

        assert reliable["cons_score"] > unreliable["cons_score"]

    def test_season_column_present(self):
        results      = self._make_results()
        races        = self._make_races()
        status       = self._make_status()
        constructors = self._make_constructors()

        bvi = compute_bvi(results, races, status, constructors)
        assert "season" in bvi.columns
        assert (bvi["season"] == 2023).all()
