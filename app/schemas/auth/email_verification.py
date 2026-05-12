from __future__ import annotations

from pydantic import BaseModel, Field


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=20)


class VerifyEmailResponse(BaseModel):
    message: str = "Email verified successfully."