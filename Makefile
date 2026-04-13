.PHONY: build up down seed test clean retrain logs shell-backend shell-db

# ── Docker ───────────────────────────────────────────────────────────────────

build:
	docker compose build

up:
	docker compose up -d
	@echo "Frontend: http://localhost:3000"
	@echo "API docs: http://localhost:8000/docs"

down:
	docker compose down

logs:
	docker compose logs -f

# ── Data & ETL ───────────────────────────────────────────────────────────────

seed:
	@echo "Running ETL pipeline..."
	docker compose run --rm backend python -m etl.transform
	docker compose run --rm backend python -m etl.load
	@echo "Seeding complete."

# ── ML Models ────────────────────────────────────────────────────────────────

retrain:
	@echo "Triggering model retraining..."
	curl -X POST http://localhost:8000/api/v1/admin/retrain
	@echo "\nRetrain job dispatched."

# ── Testing ──────────────────────────────────────────────────────────────────

test:
	docker compose run --rm backend pytest tests/ -v

test-local:
	cd backend && pytest ../tests/ -v

# ── Cleanup ──────────────────────────────────────────────────────────────────

clean:
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned up."

# ── Dev shells ───────────────────────────────────────────────────────────────

shell-backend:
	docker compose exec backend bash

shell-db:
	docker compose exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}
