# Sprint 1 — Data Acquisition and Exploratory Analysis

**Window:** 23 April 2026 – 4 May 2026
**Status:** Complete

## Goal

Establish a clean, reproducible data foundation for the project and run exploratory analysis to identify the strongest performance signals in the V6 hybrid era of Formula 1.

## Deliverables

Three Jupyter notebooks shipped to `notebooks/`:

- `01_etl_jolpica.ipynb` — ETL pipeline from the Jolpica-F1 API to a local SQLite store, with JSON caching and retry logic.
- `02_preprocessing.ipynb` — Cleaning, feature engineering, and season-level normalisation.
- `03_eda.ipynb` — Nine exploratory analyses driving Sprint 1 findings.

## Methodology

### Data acquisition
Source: [Jolpica-F1 API](https://api.jolpi.ca/ergast/), a maintained mirror of the Ergast Developer API. No third-party aggregators, no Kaggle imports. Every record is fetched live and cached locally as JSON for reproducibility. ETL uses `requests` with `tenacity` retry to handle rate limits gracefully.

### Storage
SQLite database (`pitwall.db`) with seven tables: `races`, `results`, `qualifying`, `drivers`, `constructors`, `constructor_standings`, `driver_standings`. Total coverage: 228 races, 4,626 race results, and 4,610 qualifying sessions across 11 seasons (2014–2024).

### Preprocessing
Key transformations include DNF status typing, qualifying time parsing into seconds, gap-to-pole computation, average grid position per team-season, and season-level min-max normalisation for cross-year comparison.

### EDA
Nine analyses spanning championship trends, rank stability, reliability (DNF rates), points concentration (Gini coefficient), and qualifying-points relationships. All charts saved to `reports/`.

## Key findings

**1. Qualifying speed is the strongest single predictor of season points.**
Pearson correlation r ≈ −0.79 between average qualifying gap-to-pole and total constructor points across 112 team-seasons (p < 0.001). The correlation is negative because a smaller gap to pole indicates faster qualifying, which produces more points.

**2. The era is defined by sustained constructor dominance.**
Mercedes won eight consecutive Constructors' Championships (2014–2021), followed by Red Bull in 2022 and 2023, and McLaren in 2024. This level of concentration motivates within-season normalisation in the eventual Brand Value Index.

**3. Rank volatility varies sharply across constructors:**

| Constructor  | σ (rank) | Tier          |
| ------------ | -------- | ------------- |
| Williams     | 2.83     | Most volatile |
| McLaren      | 2.44     | Volatile      |
| Mercedes     | 1.04     | Stable        |
| Red Bull     | 0.92     | Stable        |
| Force India  | 0.84     | Most stable   |

This volatility profile feeds the Consistency dimension in Sprint 3.

**4. Season concentration (Gini coefficient on constructor points)** ranges from 0.503 (2020, most competitive) to 0.619 (2016, most concentrated), with an era-wide mean of 0.556.

## Outputs

All EDA figures saved to `reports/`. Headline image: `reports/eda_06_qual_vs_points.png` (qualifying gap vs season points).

## Next steps

Sprint 2 takes the cleaned dataset and trains baseline and advanced regression models to predict end-of-season constructor points.
