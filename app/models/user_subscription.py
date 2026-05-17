from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.app_user import AppUser
    from app.models.usage_record import UsageRecord
    from app.models.prediction import Prediction
    from app.models.recommendation import Recommendation
    from app.models.subscription_change_request import SubscriptionChangeRequest
    from app.models.router import Router
    from app.models.alert import Alert
    from app.models.subscription_plan import SubscriptionPlan


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'suspended', 'expired', 'cancelled')",
            name="chk_user_subscription_status",
        ),
        Index("idx_user_subscriptions_plan_id", "plan_id"),
        Index("idx_user_subscriptions_user_id", "user_id"),
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

    plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id", ondelete="RESTRICT"),
        nullable=False,
    )

    subscription_label: Mapped[str | None] = mapped_column(String, nullable=True)

    assigned_by_admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'active'"),
    )

    auto_renew: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
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

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="user_subscriptions",
    )

    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        back_populates="user_subscriptions",
    )

    assigned_by_admin: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="assigned_user_subscriptions",
    )

    routers: Mapped[list["Router"]] = relationship(
        "Router",
        back_populates="user_subscription",
    )

    usage_records: Mapped[list["UsageRecord"]] = relationship(
        "UsageRecord",
        back_populates="user_subscription",
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction",
        back_populates="user_subscription",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="user_subscription",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="user_subscription",
    )

    subscription_change_requests: Mapped[list["SubscriptionChangeRequest"]] = relationship(
        "SubscriptionChangeRequest",
        back_populates="user_subscription",
    )
