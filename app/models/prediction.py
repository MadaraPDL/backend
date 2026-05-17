from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.app_user import AppUser
    from app.models.alert import Alert
    from app.models.recommendation import Recommendation
    from app.models.user_subscription import UserSubscription
    from app.models.subscription_plan import SubscriptionPlan

class Prediction(Base):
    __tablename__ = "predictions"

    __table_args__ = (
        Index("idx_predictions_user_id", "user_id"),
        Index("idx_predictions_user_subscription_id", "user_subscription_id"),
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

    plan_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subscription_plans.id", ondelete="SET NULL"),
        nullable=True,
    )

    prediction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
    )

    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    predicted_usage_gb: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    risk_level: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'low'"),
    )

    model_version: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="predictions",
    )

    user_subscription: Mapped["UserSubscription"] = relationship(
        "UserSubscription",
        back_populates="predictions",
    )

    plan: Mapped["SubscriptionPlan | None"] = relationship(
        "SubscriptionPlan",
        back_populates="predictions",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="prediction",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="prediction",
    )
