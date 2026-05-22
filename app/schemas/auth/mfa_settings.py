from __future__ import annotations

from pydantic import BaseModel

from app.schemas.auth.common import AccountType, MFAMethod


class MFAStatusResponse(BaseModel):
    account_type: AccountType
    mfa_required: bool
    mfa_enabled: bool
    email_mfa_enabled: bool
    authenticator_mfa_enabled: bool
    preferred_mfa_method: MFAMethod | None = None
    active_methods: list[MFAMethod]
    can_disable_email_mfa: bool
    can_disable_authenticator_mfa: bool


class PreferredMFAMethodRequest(BaseModel):
    method: MFAMethod
