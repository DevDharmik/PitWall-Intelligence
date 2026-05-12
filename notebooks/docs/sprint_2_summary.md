# Sprint 2 — Baseline and Advanced ML Models

**Window:** 5 May 2026 – 18 May 2026
**Status:** Complete

## Goal

Train and evaluate machine learning models to predict end-of-season constructor points from features available before the season ends. Compare a simple baseline against a stronger non-linear model.

## Deliverables

Three Jupyter notebooks shipped to `notebooks/`:

- `04_baseline_models.ipynb` — Linear Regression and Decision Tree baselines.
- `05_advanced_models.ipynb` — Gradient Boosting Regressor for season-points prediction.
- `06_evaluation.ipynb` — Five-fold cross-validation, held-out season test, and permutation importance.

## Methodology

### Target
Total constructor points per season — a continuous regression target.

### Features
Seven features engineered from Sprint 1 outputs: average qualifying gap-to-pole, pole count, average grid position, race-day position changes, DNF rate, and two season-context indicators.

### Train / test split
Training: 2014–2023 (ten seasons). Held-out test: 2024 (one season). The held-out season is never seen during training or cross-validation.

### Models
- **Linear Regression** — fast, interpretable, baseline.
- **Decision Tree** (depth-tuned) — captures simple non-linear effects, baseline.
- **Gradient Boosting Regressor** (`scikit-learn`) — advanced model, captures feature interactions.

### Evaluation
RMSE and R² on both five-fold cross-validation and on the held-out 2024 season. Permutation importance to measure each feature's actual contribution beyond raw feature importance.

## Key findings

**Model performance:**

| Model              | CV R² (5-fold) | Held-out 2024 R² |
| ------------------ | -------------- | ---------------- |
| Linear Regression  | ~0.82          | ~0.85            |
| Decision Tree      | ~0.78          | ~0.81            |
| Gradient Boosting  | **0.95**       | **0.96**         |

Gradient Boosting clearly wins. The model explains roughly 95 percent of the variance in season points.

**Permutation importance:**
Average grid position alone accounts for almost all the explained variance. Permuting grid position drops R² by 1.0. Permuting all six other features combined drops R² by only 0.21.

In plain terms: where a constructor starts each race tells you almost everything about how they finish the season. Race-day strategy, pit-stop performance, and reliability still matter, but only at the margins. Qualifying pace is the spine.

This finding is not novel to people inside Formula 1, but watching it fall out of the data without being told to look for it is a useful sanity check on the entire pipeline.

## Caveat

The dominance of grid position is partly genuine and partly signal leakage: grid position already encodes the underlying car pace that the other features depend on. The SHAP analysis in Sprint 3 will help disentangle direct contribution from indirect.

## Next steps

Sprint 3 adds:
- A Logistic Regression with Platt scaling for podium probability (classification target, complementing the regression).
- SHAP attribution on both the Gradient Boosting regressor and the podium classifier.
- Construction of the final Brand Value Index combining the Performance dimension (60 percent: predicted points + podium probability) with the Consistency dimension (40 percent: reliability indicators + qualifying-to-race delta).
