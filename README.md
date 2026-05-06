# PitWall Intelligence

> **Predictive Modeling of Formula 1 Constructor Performance and Sponsorship Value Using Machine Learning**

![Status](https://img.shields.io/badge/status-Sprint%202%20in%20progress-blue)
![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Capstone](https://img.shields.io/badge/M.Sc.-Capstone%202026-orange)

A data-driven Brand Value Index (BVI) for Formula 1 constructors, combining machine-learning performance prediction with SHAP-based explainability — quantifying what is currently a USD 1.8 billion sponsorship market priced largely on perception.

---

## Problem

Formula 1's sponsorship market exceeds USD 1.8 billion annually, with a global audience above 400 million viewers across broadcast, streaming, and digital channels. Yet sponsorship valuation in the sport still relies on brand-perception surveys, media-impression estimates, and subjective prestige scoring. There is no publicly available analytical framework that converts on-track performance into an interpretable, comparable, sponsor-facing metric.

## Research question

> Can explainability techniques applied to structured ML models trained on complete historical race data produce an interpretable composite score of F1 sponsorship value that discriminates between constructors?

## Brand Value Index (BVI)

Two-dimensional composite, season-normalised per constructor:

| Dimension | Weight | Components |
|---|---|---|
| **Performance** | 60% | Predicted championship points · podium probability |
| **Consistency** | 40% | Reliability indicators · qualifying-to-race delta |

Min-max normalisation within each season ensures dominant-era seasons do not suppress midfield-team scores in cross-season comparison.

## Headline finding — Sprint 1

![Qualifying pace predicts championship points](reports/eda_06_qual_vs_points.png)

Average qualifying gap-to-pole correlates with total constructor points at **Pearson r ≈ –0.79** across 112 team-seasons (p < 0.001). Qualifying pace anchors the BVI Performance dimension.

## Dataset

Single source — **[Jolpica-F1 API](https://api.jolpi.ca/ergast/)**, an actively maintained mirror of the Ergast Developer API for Formula 1. No Kaggle imports, no third-party aggregators, no synthetic data. Every record is fetched live and cached as JSON for reproducibility.

**Focal era:** V6 hybrid, 2014–2025 — stable technical regulations enabling like-for-like cross-season comparison.

| Table | Rows | Coverage |
|---|---|---|
| `races` | 228 | Grands Prix, 2014–2024 |
| `results` | 4,626 | Race finishing data |
| `qualifying` | 4,610 | Q1 / Q2 / Q3 session times |
| `constructor_standings` | 112 | Constructor-season finals |
| `driver_standings` | 247 | Driver-season finals |
| `constructors` · `drivers` | — | Team and driver metadata |

## Methodology

Jolpica API
└─► ETL (requests + tenacity, JSON cache)
└─► Preprocessing (DNF typing · qual parsing · gap-to-pole · season norm)
└─► EDA (9 analyses)
└─► Models
├─ Baseline:  Linear Regression · Decision Tree
└─ Advanced:  Gradient Boosting · Logistic Regression + Platt
└─► Evaluation (5-fold CV RMSE / R² · AUC-ROC on held-out season)
└─► SHAP attribution
└─► BVI synthesis (Performance 60% + Consistency 40%)
└─► Streamlit dashboard

## Tech stack

`Python 3.11` · `requests` · `tenacity` · `pandas` · `numpy` · `SQLite` · `scikit-learn` · `shap` · `matplotlib` · `seaborn` · `plotly` · `streamlit`

**Environment:** Google Colab · Jupyter · VS Code

## Sprint plan

| # | Window | Focus | Status |
|---|---|---|---|
| 1 | 23 Apr – 4 May | ETL pipeline · preprocessing · EDA | Complete |
| 2 | 5 May – 18 May | Baseline + advanced models | In progress |
| 3 | 19 May – 1 Jun | BVI synthesis · SHAP attribution | Planned |
| 4 | 2 Jun – 15 Jun | Streamlit dashboard | Planned |
| 5 | 16 Jun – 22 Jun | Report polish · viva prep | Planned |

**Final report due:** 22 June 2026 · **Defence:** 6 July 2026

## Sprint 1 — key findings

1. **Qualifying speed is the strongest single predictor of season points.** Pearson r ≈ –0.79 across 112 team-seasons (p < 0.001), anchoring qualifying pace as a primary Performance input.
2. **The era is defined by sustained dominance.** Mercedes won eight consecutive Constructors' Championships (2014–2021), followed by Red Bull (2022, 2023) and McLaren (2024) — concentration that motivates within-season normalisation.
3. **Constructor rank volatility varies sharply.** Williams (σ = 2.83) and McLaren (σ = 2.44) are the most volatile across the era; Force India (σ = 0.84), Red Bull (σ = 0.92), and Mercedes (σ = 1.04) are the most stable. This profile feeds the Consistency dimension.
4. **Season concentration ranges from 0.503 (2020, most competitive) to 0.619 (2016, most concentrated)**, with era-wide mean Gini 0.556.

> Numerical findings reflect current Sprint 1 notebook outputs and may be revised after end-to-end re-execution.

## Repository structure

PitWall/
├── notebooks/
│   ├── 01_etl_jolpica.ipynb       # Jolpica → SQLite, JSON caching + retry
│   ├── 02_preprocessing.ipynb     # cleaning, feature engineering, season normalisation
│   └── 03_eda.ipynb               # nine analyses driving Sprint 1 findings
├── reports/                        # EDA visual outputs (PNG, CSV)
├── data/
│   ├── pitwall.db                  # SQLite store (gitignored)
│   ├── raw/                        # cached Jolpica JSON (gitignored)
│   └── exports/
├── requirements.txt
├── LICENSE
├── .gitignore
└── README.md


## Reproducing Sprint 1

```bash
git clone https://github.com/DevDharmik/Pitwall-intelligence.git
cd Pitwall-intelligence
pip install -r requirements.txt
```

Open notebooks in order in Colab or Jupyter:
1. `notebooks/01_etl_jolpica.ipynb` — populates `data/pitwall.db` from Jolpica on first run; cached JSON in `data/raw/` is reused subsequently.
2. `notebooks/02_preprocessing.ipynb` — builds the analytical tables.
3. `notebooks/03_eda.ipynb` — generates the figures in `reports/`.

End-to-end runtime: ~10 minutes on a free Colab tier, dominated by initial Jolpica ingestion.

## Author

**Dharmik Champaneri** — Student ID 20327984
M.Sc. Data Science · University of Europe for Applied Sciences (Berlin / Potsdam)
**Supervisor:** Dr. Humera Noor Minhas
**Module:** Capstone Project · 2026

## License

[MIT License](LICENSE) for code. Reports and figures licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).


