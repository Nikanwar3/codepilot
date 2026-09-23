"""
Health endpoints.

Two separate probes on purpose, because they mean different things to an
orchestrator (ECS, k8s later):

- /live  — "is the process alive at all?" No dependency checks. If this
  fails, the orchestrator should restart the container.
- /ready — "can this instance actually serve traffic?" Checks DB and Redis
  connectivity. If this fails, the orchestrator should stop routing traffic
  to it but does NOT need to restart it (the dependency might recover).
"""

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis import get_redis
from app.db.session import get_db

router = APIRouter()


@router.get("/live", summary="Liveness probe")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
async def readiness(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict[str, object]:
    checks: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001 — surface any failure as a check result
        checks["database"] = f"error: {exc}"

    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc}"

    healthy = all(v == "ok" for v in checks.values())
    return {"status": "ok" if healthy else "degraded", "checks": checks}
