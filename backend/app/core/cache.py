"""
app/core/cache.py
─────────────────
Redis client and helper functions for BVI score caching.
All BVI results are cached with a 24-hour TTL to avoid
recomputing expensive ML inference on repeat requests.
"""

import json
import logging
import redis.asyncio as aioredis

from app.core.config import settings

log = logging.getLogger(__name__)

# ── Redis client (lazy singleton) ─────────────────────────────────────────────

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


# ── Cache helpers ─────────────────────────────────────────────────────────────

async def cache_get(key: str) -> dict | list | None:
    """Return cached value or None if missing / expired."""
    try:
        r = await get_redis()
        raw = await r.get(key)
        if raw:
            return json.loads(raw)
    except Exception as exc:
        log.warning("Cache GET failed for key=%s: %s", key, exc)
    return None


async def cache_set(key: str, value: dict | list, ttl: int | None = None) -> None:
    """Store a JSON-serialisable value with optional TTL (seconds)."""
    try:
        r = await get_redis()
        await r.set(
            key,
            json.dumps(value),
            ex=ttl or settings.bvi_cache_ttl,
        )
    except Exception as exc:
        log.warning("Cache SET failed for key=%s: %s", key, exc)


async def cache_delete(key: str) -> None:
    """Invalidate a single cache key."""
    try:
        r = await get_redis()
        await r.delete(key)
    except Exception as exc:
        log.warning("Cache DELETE failed for key=%s: %s", key, exc)


async def cache_flush_prefix(prefix: str) -> int:
    """Delete all keys matching a prefix pattern. Returns count deleted."""
    try:
        r = await get_redis()
        keys = await r.keys(f"{prefix}*")
        if keys:
            return await r.delete(*keys)
    except Exception as exc:
        log.warning("Cache FLUSH failed for prefix=%s: %s", prefix, exc)
    return 0


# ── Cache key builders ────────────────────────────────────────────────────────

def bvi_scores_key(season: int) -> str:
    return f"bvi:scores:{season}"


def bvi_compare_key(constructor_a: str, constructor_b: str, season: int) -> str:
    a, b = sorted([constructor_a.lower(), constructor_b.lower()])
    return f"bvi:compare:{a}:{b}:{season}"


def constructor_rankings_key(season: int) -> str:
    return f"constructors:rankings:{season}"


def sponsorship_tiers_key(season: int) -> str:
    return f"sponsorship:tiers:{season}"


def season_comparison_key(constructor: str) -> str:
    return f"season:comparison:{constructor.lower()}"
