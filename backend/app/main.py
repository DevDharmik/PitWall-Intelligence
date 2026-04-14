"""
app/main.py
───────────
FastAPI application entry point.
Mounts all routers, configures CORS, and handles startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.services.ml_registry import ml_registry

from app.api import bvi, constructors, drivers, seasons, circuits, predict, admin

# ── App init ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="PitWall Intelligence API",
    description="F1 Sponsorship Value Analytics — Brand Value Index engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup / shutdown ────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    # Create tables if they don't exist (idempotent)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Pre-load ML models into memory
    ml_registry.load_all()


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


# ── Routers ───────────────────────────────────────────────────────────────────

PREFIX = "/api/v1"

app.include_router(bvi.router,          prefix=PREFIX, tags=["BVI"])
app.include_router(constructors.router, prefix=PREFIX, tags=["Constructors"])
app.include_router(drivers.router,      prefix=PREFIX, tags=["Drivers"])
app.include_router(seasons.router,      prefix=PREFIX, tags=["Seasons"])
app.include_router(circuits.router,     prefix=PREFIX, tags=["Circuits"])
app.include_router(predict.router,      prefix=PREFIX, tags=["Predictions"])
app.include_router(admin.router,        prefix=PREFIX, tags=["Admin"])


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}
