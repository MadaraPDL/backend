from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user_subscription import UserSubscription 
    from app.models.user_subscription import UserSubscription
    from app.models.recommendation import Recommendation
    from app.models.admin import Admin
    from app.models.subscription_plan import SubscriptionPlan
    from app.models.app_user import AppUser

class SubscriptionChangeRequest(Base):
    __tablename__ = "subscription_change_requests"

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

    current_plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )

    requested_plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )

    recommendation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recommendations.id"),
        nullable=True,
    )

    request_type: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'pending'"),
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    reviewed_by_admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id"),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    admin_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="subscription_change_requests",
    )

    user_subscription: Mapped["UserSubscription"] = relationship(
        "UserSubscription",
        back_populates="subscription_change_requests",
    )

    current_plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        foreign_keys=[current_plan_id],
        back_populates="current_plan_change_requests",
    )

    requested_plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan",
        foreign_keys=[requested_plan_id],
        back_populates="requested_plan_change_requests",
    )

    recommendation: Mapped["Recommendation | None"] = relationship(
        "Recommendation",
        back_populates="subscription_change_requests",
    )

    reviewed_by_admin: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="reviewed_subscription_change_requests",
    )