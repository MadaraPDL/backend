from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.device import Device
    from app.models.alert import Alert
    from app.models.user_subscription import UserSubscription
    from app.models.app_user import AppUser
    from app.models.router import Router


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("app_users.id"),
        nullable=False,
    )

    user_subscription_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_subscriptions.id"),
        nullable=False,
    )

    router_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("routers.id"),
        nullable=False,
    )

    device_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=True,
    )

    upload_mb: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
        server_default=text("0"),
    )

    download_mb: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
        server_default=text("0"),
    )

    total_mb: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    record_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    record_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        server_default=text("'router'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="usage_records",
    )

    user_subscription: Mapped["UserSubscription"] = relationship(
        "UserSubscription",
        back_populates="usage_records",
    )

    router: Mapped["Router"] = relationship(
        "Router",
        back_populates="usage_records",
    )

    device: Mapped["Device | None"] = relationship(
        "Device",
        back_populates="usage_records",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="usage_record",
    )