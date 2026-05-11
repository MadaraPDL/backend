from __future__ import annotations
from datetime import datetime, timedelta, timezone

from typing import TypeAlias

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
    )
from app.models.email_verification_token import EmailVerificationToken
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType, MFAMethod
from app.models.account_invitation import AccountInvitation
from app.models.password_reset_token import PasswordResetToken
from app.services.mfa_service import (
    create_mfa_challenge,
    get_mfa_challenge_by_token,
    verify_mfa_challenge_code,
    
    )

Account: TypeAlias = Admin | AppUser

def normalize_identifier(identifier: str) -> str:
    return identifier.strip().lower()

async def get_account_by_identifier(
        db: AsyncSession,
        account_type: AccountType,
        identifier: str,
) -> Account | None:
     normalized_identifier = normalize_identifier(identifier)

     model = Admin if account_type == "admin" else AppUser

     stmt = select(model).where(
          or_(
               func.lower(model.email) == normalized_identifier,
               func.lower(model.username) == normalized_identifier,
          )
     )

     result = await db.execute(stmt)
     return result.scalar_one_or_none()

async def authenticate_account(
          db: AsyncSession,
          account_type: AccountType,
          identifier: str,
          password: str,
) -> Account | None:
     account = await get_account_by_identifier(
          db=db,
          account_type=account_type,
          identifier=identifier,
     )
     if account is None:
          return None
     
     if not verify_password(password, account.password_hash):
          return None
     
     if account.status != "active":
          return None
     
     return account

def build_auth_token_response(
          account: Account,
          account_type: AccountType,
) -> dict:
     access_token = create_access_token(
          subject=account.id,
          account_type=account_type,
     )

     return {
          "access_token": access_token,
          "token_type": "bearer",
          "account_type": account_type,
          "account_id":account.id,
          "full_name": account.full_name,
          "email": account.email,
          "role": account.role if account_type == "admin" else None,
     }
 
def get_default_mfa_method(account_type: AccountType) -> MFAMethod:
     return "authenticator" if account_type == "admin" else "email"

def get_account_mfa_method(
          account: Account,
          account_type: AccountType,
) -> MFAMethod:
     if account.preferred_mfa_method in ("email", "authenticator"):
          return account.preferred_mfa_method
     
     return get_default_mfa_method(account_type)

async def start_login(
          db: AsyncSession,
          account_type: AccountType,
          identifier: str,
          password: str,
) -> tuple[dict, str | None] | None:
     account = await authenticate_account(
          db=db,
          account_type=account_type,
          identifier=identifier,
          password=password,
     )

     if account is None:
          return None
     
     if not account.mfa_enabled:
          return build_auth_token_response(
               account=account,
               account_type=account_type,
          ), None
     
     method = get_account_mfa_method(
          account=account,
          account_type=account_type,
     )

     challenge, raw_challenge_token, raw_email_code = await create_mfa_challenge(
          db=db,
          account=account,
          account_type=account_type,
          method=method,
     )


     return {
          "mfa_required": True,
          "challenge_token": raw_challenge_token,
          "method": method,
          "expires_at": challenge.expires_at,
          "message": "MFA verification is required to complete login."
     }, raw_email_code 

async def complete_mfa_login(
          db:AsyncSession,
          challenge_token:str,
          code:str,
) -> dict | None:
     challenge = await get_mfa_challenge_by_token(
          db=db,
          raw_challenge_token=challenge_token,
     )

     if challenge is None:
          return None
     

     account = await verify_mfa_challenge_code(
          db=db,
          challenge=challenge,
          code=code,
     )

     if account is None:
          return None
     
     return build_auth_token_response(
          account=account,
          account_type=challenge.account_type,
     )

async def get_invitation_by_token(
    db: AsyncSession,
    raw_token: str,
) -> AccountInvitation | None:
    token_hash = hash_token(raw_token)

    stmt = select(AccountInvitation).where(
        AccountInvitation.token_hash == token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_invitation_active(invitation: AccountInvitation) -> bool:
    now = datetime.now(timezone.utc)

    if invitation.accepted_at is not None:
        return False

    if invitation.revoked_at is not None:
        return False

    if invitation.expires_at <= now:
        return False

    return True


async def accept_invitation(
    db: AsyncSession,
    raw_token: str,
    username: str,
    password: str,
    preferred_mfa_method: MFAMethod | None = None,
) -> Account | None:
    invitation = await get_invitation_by_token(
        db=db,
        raw_token=raw_token,
    )

    if invitation is None:
        return None

    if not is_invitation_active(invitation):
        return None

    existing_email_account = await get_account_by_identifier(
        db=db,
        account_type=invitation.account_type,
        identifier=invitation.email,
    )

    if existing_email_account is not None:
        return None

    existing_username_account = await get_account_by_identifier(
        db=db,
        account_type=invitation.account_type,
        identifier=username,
    )

    if existing_username_account is not None:
        return None

    now = datetime.now(timezone.utc)

    selected_mfa_method = (
        preferred_mfa_method
        if preferred_mfa_method in ("email", "authenticator")
        else get_default_mfa_method(invitation.account_type)
    )

    password_hash = hash_password(password)

    if invitation.account_type == "admin":
        account = Admin(
            isp_id=invitation.isp_id,
            full_name=invitation.full_name or invitation.email,
            email=invitation.email,
            username=username,
            password_hash=password_hash,
            role=invitation.admin_role or "isp_admin",
            status="active",
            created_by_admin_id=invitation.invited_by_admin_id,
            email_verified_at=now,
            password_changed_at=now,
            mfa_enabled=False,
            mfa_required=True,
            preferred_mfa_method=selected_mfa_method,
        )
    else:
        if invitation.isp_id is None:
            return None

        account = AppUser(
            isp_id=invitation.isp_id,
            full_name=invitation.full_name or invitation.email,
            email=invitation.email,
            username=username,
            password_hash=password_hash,
            status="active",
            created_by_admin_id=invitation.invited_by_admin_id,
            email_verified_at=now,
            password_changed_at=now,
            mfa_enabled=False,
            mfa_required=False,
            preferred_mfa_method=selected_mfa_method,
        )

    invitation.accepted_at = now

    db.add(account)
    await db.flush()

    return account


async def create_password_reset_token(
    db: AsyncSession,
    account_type: AccountType,
    identifier: str,
) -> str | None:
    account = await get_account_by_identifier(
        db=db,
        account_type=account_type,
        identifier=identifier,
    )

    if account is None:
        return None

    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    if account_type == "admin":
        reset_token = PasswordResetToken(
            account_type=account_type,
            admin_id=account.id,
            app_user_id=None,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
    else:
        reset_token = PasswordResetToken(
            account_type=account_type,
            admin_id=None,
            app_user_id=account.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )

    db.add(reset_token)
    await db.flush()

    return raw_token


async def get_password_reset_token(
    db: AsyncSession,
    raw_token: str,
) -> PasswordResetToken | None:
    token_hash = hash_token(raw_token)

    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token_hash == token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_password_reset_token_active(reset_token: PasswordResetToken) -> bool:
    now = datetime.now(timezone.utc)

    if reset_token.used_at is not None:
        return False

    if reset_token.expires_at <= now:
        return False

    return True


async def reset_password_with_token(
    db: AsyncSession,
    raw_token: str,
    new_password: str,
) -> Account | None:
    reset_token = await get_password_reset_token(
        db=db,
        raw_token=raw_token,
    )

    if reset_token is None:
        return None

    if not is_password_reset_token_active(reset_token):
        return None

    if reset_token.account_type == "admin":
        if reset_token.admin_id is None:
            return None

        account = await db.get(Admin, reset_token.admin_id)
    else:
        if reset_token.app_user_id is None:
            return None

        account = await db.get(AppUser, reset_token.app_user_id)

    if account is None:
        return None

    now = datetime.now(timezone.utc)

    account.password_hash = hash_password(new_password)
    account.password_changed_at = now
    reset_token.used_at = now

    await db.flush()

    return account


async def create_email_verification_token(
    db: AsyncSession,
    account: Account,
    account_type: AccountType,
) -> str:
    raw_token = generate_secure_token()
    token_hash = hash_token(raw_token)

    verification_token = EmailVerificationToken(
        account_type=account_type,
        admin_id=account.id if account_type == "admin" else None,
        app_user_id=account.id if account_type == "app_user" else None,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(verification_token)
    await db.flush()

    return raw_token


async def get_email_verification_token(
    db: AsyncSession,
    raw_token: str,
) -> EmailVerificationToken | None:
    token_hash = hash_token(raw_token)

    stmt = select(EmailVerificationToken).where(
        EmailVerificationToken.token_hash == token_hash
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def is_email_verification_token_active(
    verification_token: EmailVerificationToken,
) -> bool:
    now = datetime.now(timezone.utc)

    if verification_token.used_at is not None:
        return False

    if verification_token.expires_at <= now:
        return False

    return True


async def verify_email_with_token(
    db: AsyncSession,
    raw_token: str,
) -> Account | None:
    verification_token = await get_email_verification_token(
        db=db,
        raw_token=raw_token,
    )

    if verification_token is None:
        return None

    if not is_email_verification_token_active(verification_token):
        return None

    if verification_token.account_type == "admin":
        if verification_token.admin_id is None:
            return None

        account = await db.get(Admin, verification_token.admin_id)
    else:
        if verification_token.app_user_id is None:
            return None

        account = await db.get(AppUser, verification_token.app_user_id)

    if account is None:
        return None

    now = datetime.now(timezone.utc)

    account.email_verified_at = now
    verification_token.used_at = now

    await db.flush()

    return account
