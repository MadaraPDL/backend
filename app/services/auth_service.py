from __future__ import annotations

from typing import TypeAlias

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.models.admin import Admin
from app.models.app_user import AppUser
from app.schemas.auth import AccountType, MFAMethod
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