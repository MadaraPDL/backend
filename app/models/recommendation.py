from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.prediction import Prediction
    from app.models.user_subscription import UserSubscription
    from app.models.subscription_change_request import SubscriptionChangeRequest
    from app.models.app_user import AppUser
    from app.models.subscription_plan import SubscriptionPlan


class Recommendation(Base):
    __tablename__ = "recommendations"

    __table_args__ = (
        CheckConstraint(
            "recommendation_type IN ("
            "'upgrade_plan', "
            "'downgrade_plan', "
            "'stay_current', "
            "'monitor_usage'"
            ")",
            name="chk_recommendation_type",
        ),
        CheckConstraint(
            "status IN ('new', 'accepted')",
            name="chk_recommendation_status",
        ),
        Index("idx_recommendations_user_id", "user_id"),
        Index("idx_recommendations_user_subscription_id", "user_subscription_id"),
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
        ForeignKey("user_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
    )

    current_plan_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id", ondelete="SET NULL"),
        nullable=True,
    )

    recommendation_plan_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id", ondelete="SET NULL"),
        nullable=True,
    )

    prediction_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="SET NULL"),
        nullable=True,
    )

    recommendation_type: Mapped[str] = mapped_column(String, nullable=False)
    recommendation_text: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'new'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="recommendations",
    )

    user_subscription: Mapped["UserSubscription"] = relationship(
        "UserSubscription",
        back_populates="recommendations",
    )

    current_plan: Mapped["SubscriptionPlan | None"] = relationship(
        "SubscriptionPlan",
        foreign_keys=[current_plan_id],
        back_populates="current_plan_recommendations",
    )

    recommendation_plan: Mapped["SubscriptionPlan | None"] = relationship(
        "SubscriptionPlan",
        foreign_keys=[recommendation_plan_id],
        back_populates="recommended_plan_recommendations",
    )

    prediction: Mapped["Prediction | None"] = relationship(
        "Prediction",
        back_populates="recommendations",
    )

    subscription_change_requests: Mapped[list["SubscriptionChangeRequest"]] = relationship(
        "SubscriptionChangeRequest",
        back_populates="recommendation",
    )
