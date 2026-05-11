from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.alert import Alert
    from app.models.device import Device
    from app.models.device_network_policy import DeviceNetworkPolicy
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.isp import ISP
    from app.models.mfa_backup_code import MFABackupCode
    from app.models.mfa_challenge import MFAChallenge
    from app.models.password_reset_token import PasswordResetToken
    from app.models.prediction import Prediction
    from app.models.recommendation import Recommendation
    from app.models.subscription_change_request import SubscriptionChangeRequest
    from app.models.usage_record import UsageRecord
    from app.models.user_subscription import UserSubscription


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    isp_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("isps.id"),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)

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

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
        server_default=text("false"),
    )

    mfa_secret: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_mfa_method: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        server_default=text("'email'"),
    )

    isp: Mapped["ISP"] = relationship(
        "ISP",
        back_populates="app_users",
    )

    creator: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="created_app_users",
    )

    user_subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="user",
    )

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="user",
    )

    usage_records: Mapped[list["UsageRecord"]] = relationship(
        "UsageRecord",
        back_populates="user",
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction",
        back_populates="user",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="user",
    )

    requested_device_network_policies: Mapped[list["DeviceNetworkPolicy"]] = relationship(
        "DeviceNetworkPolicy",
        back_populates="requested_by_user",
    )

    subscription_change_requests: Mapped[list["SubscriptionChangeRequest"]] = relationship(
        "SubscriptionChangeRequest",
        back_populates="user",
    )

    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="app_user",
    )

    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="app_user",
    )

    mfa_backup_codes: Mapped[list["MFABackupCode"]] = relationship(
        "MFABackupCode",
        back_populates="app_user",
    )

    mfa_challenges: Mapped[list["MFAChallenge"]] = relationship(
        "MFAChallenge",
        back_populates="app_user",
    )