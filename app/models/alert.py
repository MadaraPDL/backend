from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.prediction import Prediction
    from app.models.user_subscription import UserSubscription
    from app.models.device import Device
    from app.models.app_user import AppUser
    from app.models.device_connection_log import DeviceConnectionLog
    from app.models.usage_record import UsageRecord

class Alert(Base):
    __tablename__ = "alerts"

    __table_args__ = (
        CheckConstraint(
            "alert_type IN ("
            "'high_usage', "
            "'plan_exceed_risk', "
            "'unusual_consumption', "
            "'new_device_connected', "
            "'policy_failed'"
            ")",
            name="chk_alert_type",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="chk_alert_severity",
        ),
        Index("idx_alerts_status", "status"),
        Index("idx_alerts_user_id", "user_id"),
        Index("idx_alerts_user_subscription_id", "user_subscription_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_subscription_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_subscriptions.id", ondelete="SET NULL"),
        nullable=False,
    )

    device_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
    )

    connection_log_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("device_connection_logs.id", ondelete="SET NULL"),
        nullable=True,
    )

    usage_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usage_records.id", ondelete="SET NULL"),
        nullable=True,
    )

    prediction_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="SET NULL"),
        nullable=True,
    )

    alert_type: Mapped[str] = mapped_column(String, nullable=False)

    severity: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'medium'"),
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'unread'"),
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="alerts",
    )

    user_subscription: Mapped["UserSubscription"] = relationship(
        "UserSubscription",
        back_populates="alerts",
    )

    device: Mapped["Device | None"] = relationship(
        "Device",
        back_populates="alerts",
    )

    connection_log: Mapped["DeviceConnectionLog | None"] = relationship(
        "DeviceConnectionLog",
        back_populates="alerts",
    )

    usage_record: Mapped["UsageRecord | None"] = relationship(
        "UsageRecord",
        back_populates="alerts",
    )

    prediction: Mapped["Prediction | None"] = relationship(
        "Prediction",
        back_populates="alerts",
    )
