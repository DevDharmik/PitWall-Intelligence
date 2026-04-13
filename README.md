# PitWall Intelligence
### F1 Sponsorship Value Analytics Platform

> Quantifying sponsorship ROI in Formula 1 through machine learning & the Brand Value Index (BVI).

**Student:** Dharmik Champaneri | **ID:** 20327984  
**Programme:** M.Sc. Data Science — University of Europe for Applied Sciences  
**Supervisor:** Dr. Humera Noor

---

## What It Does

PitWall Intelligence scores every F1 constructor's **sponsorship attractiveness** using a composite Brand Value Index (BVI):

```
BVI = Performance × 0.40 + Consistency × 0.30 + Exposure × 0.30
```

| Dimension | Weight | Key Signals |
|---|---|---|
| Performance | 40% | Championship points, race wins, podium rate |
| Consistency | 30% | DNF rate, points-finish rate, quali→race delta |
| Exposure | 30% | Podium appearances, broadcast proxy, circuit weight |

Constructors are classified into **Tier 1 (BVI ≥ 75)**, **Tier 2 (50–75)**, or **Tier 3 (< 50)**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Recharts, Tailwind CSS, React Router v6 |
| API Backend | FastAPI (Python 3.11), Pydantic v2, Uvicorn |
| ML Layer | scikit-learn, pandas, NumPy, joblib |
| Database | PostgreSQL 15 |
| Cache | Redis 7 (24hr TTL on BVI scores) |
| Container | Docker + Docker Compose |
| ETL | Python + psycopg2 |
| Testing | pytest, httpx |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local dev)
- Node.js 18+ (for local frontend dev)

### 1. Clone & configure
```bash
git clone https://github.com/your-username/pitwall-intelligence.git
cd pitwall-intelligence
cp .env.example .env
# Edit .env with your credentials
```

### 2. Add the data
Download the [Kaggle F1 dataset](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) and place all CSVs in `data/raw/`.

### 3. One-command launch
```bash
make build      # Build all Docker images
make seed       # Run ETL: load CSVs → PostgreSQL, compute BVI scores
make up         # Start all services
```

- **Frontend:** http://localhost:3000  
- **API docs:** http://localhost:8000/docs  
- **API base:** http://localhost:8000/api/v1

### Other make targets
```bash
make test       # Run pytest suite
make clean      # Stop containers + remove volumes
make retrain    # Trigger ML model retraining
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/bvi/scores` | GET | BVI scores for all constructors in a season |
| `/api/v1/bvi/compare` | GET | Side-by-side comparison of two constructors |
| `/api/v1/constructors/rankings` | GET | Championship standings + ML-adjusted metrics |
| `/api/v1/drivers/analytics/{id}` | GET | Driver-level performance deep-dive |
| `/api/v1/season/comparison` | GET | Year-over-year BVI trend data |
| `/api/v1/circuits/{id}/performance` | GET | Circuit-specific constructor stats |
| `/api/v1/predict/podium` | POST | Podium probability prediction |
| `/api/v1/sponsorship/tiers` | GET | Tier 1/2/3 constructor classification |
| `/api/v1/admin/retrain` | POST | Trigger background model retraining |

---

## Dashboard Tabs

1. **BVI Overview** — Radar chart of all three BVI dimensions per constructor
2. **Constructor Rankings** — Full leaderboard with ML-adjusted performance column
3. **Driver Analytics** — Qualifying vs race pace scatter, points trajectory, DNF breakdown
4. **Season Comparison** — Multi-season BVI trend lines
5. **Circuit Intelligence** — Constructor win rates and finishing positions by venue
6. **Podium Predictor** — Live probability estimate given race conditions
7. **Sponsorship Tiers** — Tier 1/2/3 grid with downloadable summary

---

## Project Structure

```
pitwall-intelligence/
├── backend/           # FastAPI app
├── frontend/          # React SPA
├── etl/               # Data ingestion scripts
├── data/raw/          # Kaggle CSVs (not committed)
├── data/processed/    # Computed BVI scores
├── ml_models/         # Serialised joblib models
├── notebooks/         # EDA + model training
├── tests/             # pytest suite
├── docker-compose.yml
└── Makefile
```

---

## Data Sources

- [Kaggle F1 World Championship Dataset](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) — 1950–2024 race history
- [Ergast Developer API](https://ergast.com/mrd/) — supplementary live race records

---

## License

MIT — see `LICENSE`
