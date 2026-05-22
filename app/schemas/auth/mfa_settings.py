from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.auth.common import AccountType, MFAMethod


MFASettingsAction = Literal[
    "enable_email",
    "disable_email",
    "disable_authenticator",
    "prefer_email",
    "prefer_authenticator",
]


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


class MFASettingsChallengeRequest(BaseModel):
    method: MFAMethod


class MFASettingsChallengeResponse(BaseModel):
    challenge_token: str
    method: MFAMethod
    expires_at: datetime
    message: str
    dev_email_code: str | None = None


class MFASettingsActionRequest(BaseModel):
    action: MFASettingsAction
    challenge_token: str = Field(..., min_length=20)
    code: str = Field(..., min_length=6, max_length=32)

class MFABackupCodeStatusResponse(BaseModel):
    account_type: AccountType
    backup_codes_available: bool
    available_backup_code_count: int


class MFABackupCodesRegenerateRequest(BaseModel):
    challenge_token: str = Field(..., min_length=20)
    code: str = Field(..., min_length=6, max_length=32)


class MFABackupCodesRegenerateResponse(BaseModel):
    account_type: AccountType
    backup_codes_available: bool
    available_backup_code_count: int
    backup_codes: list[str]
    message: str = (
        "Store these backup codes now. They are shown only once and only hashes "
        "are stored by PulseFi."
    )
