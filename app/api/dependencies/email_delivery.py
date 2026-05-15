from fastapi import HTTPException, status

from app.core.config import settings


def require_email_delivery_for_production() -> None:
    if settings.DEBUG or settings.EMAIL_DELIVERY_ENABLED:
        return

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "Email delivery is not configured. Configure email delivery before "
            "using token-based email flows in production."
        ),
    )
