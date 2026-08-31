from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_cache
from app.services.cache import CacheBackend

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db), cache: CacheBackend = Depends(get_cache)) -> dict:
    settings = get_settings()
    postgres = "ok"
    redis = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        postgres = f"error: {exc}"
    try:
        if hasattr(cache, "client"):
            cache.client.ping()
        else:
            cache.get_json("vernier:health")
            redis = "memory"
    except Exception as exc:
        redis = f"error: {exc}"
    return {
        "status": "ok" if postgres == "ok" else "degraded",
        "postgres": postgres,
        "redis": redis,
        "llm": "configured" if settings.llm_api_key else "heuristic-only",
        "model": settings.llm_model,
    }
