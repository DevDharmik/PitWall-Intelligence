"""
app/api/admin.py
────────────────
Admin endpoints:
  POST /api/v1/admin/retrain — trigger background ML model retraining
"""

from fastapi import APIRouter, BackgroundTasks
from app.services.ml_registry import ml_registry
from app.core.cache import cache_flush_prefix
from app.models.schemas import RetrainResponse

router = APIRouter()


def _retrain_job():
    """
    Background task — reloads ML models from disk.
    In production this would re-run the training pipeline
    and serialise fresh models before reloading.
    """
    ml_registry.reload()


@router.post("/admin/retrain", response_model=RetrainResponse)
async def retrain(background_tasks: BackgroundTasks):
    """
    Trigger a background ML model retrain job.
    Also flushes the BVI Redis cache so stale scores are not served
    after the new models are loaded.

    The endpoint returns immediately — retraining runs asynchronously.
    Monitor logs for 'ML models reloaded' confirmation.
    """
    # Flush all BVI-related cache keys
    await cache_flush_prefix("bvi:")
    await cache_flush_prefix("constructors:")
    await cache_flush_prefix("sponsorship:")
    await cache_flush_prefix("season:")

    # Dispatch retrain as a background task
    background_tasks.add_task(_retrain_job)

    return RetrainResponse(
        status="accepted",
        message=(
            "Retrain job dispatched. Models will reload on completion. "
            "Redis cache has been flushed."
        ),
    )
