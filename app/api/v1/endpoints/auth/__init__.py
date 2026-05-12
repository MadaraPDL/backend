from fastapi import APIRouter

from app.api.v1.endpoints.auth import(
    email_verification,
    invitations,
    login,
    mfa,
    password_reset,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(login.router)
router.include_router(mfa.router)
router.include_router(invitations.router)
router.include_router(password_reset.router)
router.include_router(email_verification.router)