from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.prediction import Prediction
    from app.models.recommendation import Recommendation
    from app.models.subscription_change_request import SubscriptionChangeRequest
    from app.models.user_subscription import UserSubscription
    from app.models.isp import ISP
   


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    __table_args__ = (
        UniqueConstraint("isp_id", "plan_name"),
    )

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

    plan_name: Mapped[str] = mapped_column(String, nullable=False)

    monthly_price: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
        server_default=text("0"),
    )

    data_limit_gb: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    speed_limit_mbps: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
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

    isp: Mapped["ISP"] = relationship(
        "ISP",
        back_populates="subscription_plans",
    )

    creator: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="created_subscription_plans",
    )

    user_subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="plan",
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction",
        back_populates="plan",
    )

    current_plan_recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        foreign_keys="Recommendation.current_plan_id",
        back_populates="current_plan",
    )

    recommended_plan_recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        foreign_keys="Recommendation.recommendation_plan_id",
        back_populates="recommendation_plan",
    )

    current_plan_change_requests: Mapped[list["SubscriptionChangeRequest"]] = relationship(
        "SubscriptionChangeRequest",
        foreign_keys="SubscriptionChangeRequest.current_plan_id",
        back_populates="current_plan",
    )

    requested_plan_change_requests: Mapped[list["SubscriptionChangeRequest"]] = relationship(
        "SubscriptionChangeRequest",
        foreign_keys="SubscriptionChangeRequest.requested_plan_id",
        back_populates="requested_plan",
    )