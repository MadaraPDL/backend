from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies.rate_limit import reset_rate_limit_state
from app.core.config import settings

router = APIRouter(prefix="/rate-limit", include_in_schema=False)


@router.post("/reset")
async def reset_auth_rate_limit_for_local_dev() -> dict[str, str]:
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    reset_rate_limit_state()

    return {"message": "Local development auth rate limit state reset."}
