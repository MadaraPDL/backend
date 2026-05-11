from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account_invitation import AccountInvitation
    from app.models.app_user import AppUser
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.isp import ISP
    from app.models.mfa_backup_code import MFABackupCode
    from app.models.mfa_challenge import MFAChallenge
    from app.models.password_reset_token import PasswordResetToken
    from app.models.report import Report
    from app.models.router import Router
    from app.models.subscription_change_request import SubscriptionChangeRequest
    from app.models.subscription_plan import SubscriptionPlan
    from app.models.user_subscription import UserSubscription


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    isp_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("isps.id"),
        nullable=True,
    )

    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'active'"),
    )

    created_by_admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    username: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    mfa_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    mfa_secret: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_mfa_method: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        server_default=text("'authenticator'"),
    )

    isp: Mapped["ISP | None"] = relationship(
        "ISP",
        foreign_keys=[isp_id],
        back_populates="admins",
    )

    creator: Mapped["Admin | None"] = relationship(
        "Admin",
        remote_side=[id],
        foreign_keys=[created_by_admin_id],
        back_populates="created_admins",
    )

    created_admins: Mapped[list["Admin"]] = relationship(
        "Admin",
        foreign_keys=[created_by_admin_id],
        back_populates="creator",
    )

    created_isps: Mapped[list["ISP"]] = relationship(
        "ISP",
        foreign_keys="ISP.created_by_admin_id",
        back_populates="creator",
    )

    created_app_users: Mapped[list["AppUser"]] = relationship(
        "AppUser",
        back_populates="creator",
    )

    created_subscription_plans: Mapped[list["SubscriptionPlan"]] = relationship(
        "SubscriptionPlan",
        back_populates="creator",
    )

    assigned_user_subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="assigned_by_admin",
    )

    assigned_routers: Mapped[list["Router"]] = relationship(
        "Router",
        back_populates="assigned_by_admin",
    )

    reviewed_subscription_change_requests: Mapped[list["SubscriptionChangeRequest"]] = relationship(
        "SubscriptionChangeRequest",
        back_populates="reviewed_by_admin",
    )

    generated_reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="generated_by_admin",
    )

    sent_account_invitations: Mapped[list["AccountInvitation"]] = relationship(
        "AccountInvitation",
        back_populates="invited_by_admin",
    )

    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="admin",
    )

    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="admin",
    )

    mfa_backup_codes: Mapped[list["MFABackupCode"]] = relationship(
        "MFABackupCode",
        back_populates="admin",
    )

    mfa_challenges: Mapped[list["MFAChallenge"]] = relationship(
        "MFAChallenge",
        back_populates="admin",
    )