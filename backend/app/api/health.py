from typing import Any

from fastapi import APIRouter
from redis import Redis

from app.core.config import settings
from app.db.session import check_database

router = APIRouter(tags=["health"])


def check_redis() -> bool:
    client = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
    try:
        return bool(client.ping())
    finally:
        client.close()


@router.get("/health")
def health_check() -> dict[str, Any]:
    checks: dict[str, bool] = {"database": False, "redis": False}

    try:
        checks["database"] = check_database()
    except Exception:
        checks["database"] = False

    try:
        checks["redis"] = check_redis()
    except Exception:
        checks["redis"] = False

    service_ok = all(checks.values())

    return {
        "status": "ok" if service_ok else "degraded",
        "service": settings.app_name,
        "environment": settings.app_env,
        "checks": checks,
    }
