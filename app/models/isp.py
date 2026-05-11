from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.app_user import AppUser
    from app.models.router import Router
    from app.models.report import Report
    from app.models.subscription_plan import SubscriptionPlan

class ISP(Base):
    __tablename__ = "isps"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    creator: Mapped["Admin | None"] = relationship(
        "Admin",
        foreign_keys=[created_by_admin_id],
        back_populates="created_isps",
    )

    admins: Mapped[list["Admin"]] = relationship(
        "Admin",
        foreign_keys="Admin.isp_id",
        back_populates="isp",
    )

    app_users: Mapped[list["AppUser"]] = relationship(
        "AppUser",
        back_populates="isp",
    )

    subscription_plans: Mapped[list["SubscriptionPlan"]] = relationship(
        "SubscriptionPlan",
        back_populates="isp",
    )

    routers: Mapped[list["Router"]] = relationship(
        "Router",
        back_populates="isp"
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="isp",
    )