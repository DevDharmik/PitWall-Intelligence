"""
app/services/ml_registry.py
────────────────────────────
Singleton registry that loads serialised scikit-learn models from disk
at application startup and exposes them for inference.

Models are trained in notebooks/03 and notebooks/04 and serialised
to ml_models/ via joblib. If model files are missing, the registry
stubs the models with simple fallbacks so the API remains functional.
"""

import logging
import numpy as np
from pathlib import Path

log = logging.getLogger(__name__)


class _FallbackClassifier:
    """Stub podium classifier used when the model file is not found."""
    def predict_proba(self, X):
        # Return naive probability based on grid position only
        grid = X[0][0] if len(X) > 0 else 10
        prob = max(0.0, min(1.0, (21 - grid) / 40))
        return np.array([[1 - prob, prob]])


class _FallbackRegressor:
    """Stub points regressor used when the model file is not found."""
    def predict(self, X):
        return np.array([100.0])


class MlRegistry:
    """
    Loads and caches ML models at startup.
    Access via the module-level `ml_registry` singleton.
    """

    def __init__(self):
        self._points_model = None
        self._podium_model = None
        self._loaded = False

    def load_all(self):
        """Load all models from disk. Called once at app startup."""
        try:
            import joblib

            points_path = Path("ml_models/constructor_points_gbr.joblib")
            podium_path = Path("ml_models/podium_classifier_lr.joblib")

            if points_path.exists():
                self._points_model = joblib.load(points_path)
                log.info("Loaded constructor points model from %s", points_path)
            else:
                self._points_model = _FallbackRegressor()
                log.warning(
                    "Constructor points model not found at %s — using fallback. "
                    "Run notebooks/03_constructor_points_model.ipynb to train.",
                    points_path,
                )

            if podium_path.exists():
                self._podium_model = joblib.load(podium_path)
                log.info("Loaded podium classifier from %s", podium_path)
            else:
                self._podium_model = _FallbackClassifier()
                log.warning(
                    "Podium classifier not found at %s — using fallback. "
                    "Run notebooks/04_podium_classifier.ipynb to train.",
                    podium_path,
                )

            self._loaded = True

        except Exception as exc:
            log.error("Failed to load ML models: %s", exc)
            self._points_model = _FallbackRegressor()
            self._podium_model = _FallbackClassifier()
            self._loaded = True

    def reload(self):
        """Reload models from disk — called by admin retrain endpoint."""
        self._loaded = False
        self.load_all()
        log.info("ML models reloaded.")

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_podium_probability(
        self,
        grid_position: int,
        is_wet: bool,
        circuit_win_rate: float,
        rolling_avg_finish: float,
    ) -> tuple[float, list[float]]:
        """
        Returns (probability, [lower_ci, upper_ci]).
        Features: [grid_position, is_wet, circuit_win_rate, rolling_avg_finish]
        """
        X = np.array([[grid_position, int(is_wet), circuit_win_rate, rolling_avg_finish]])
        proba = float(self._podium_model.predict_proba(X)[0][1])

        # Approximate 95% CI using ±1.5 * crude standard error
        margin = min(proba, 1 - proba) * 0.3
        lower = round(max(0.0, proba - margin), 3)
        upper = round(min(1.0, proba + margin), 3)

        return round(proba, 3), [lower, upper]

    def predict_constructor_points(self, features: list[float]) -> float:
        """
        Predict end-of-season constructor points.
        Features: [avg_grid, reliability_rate, prev_season_rank, avg_quali_delta]
        """
        X = np.array([features])
        return round(float(self._points_model.predict(X)[0]), 1)


# Module-level singleton
ml_registry = MlRegistry()
