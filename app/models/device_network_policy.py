from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.app_user import AppUser
    from app.models.router import Router
    from app.models.router_action_log import RouterActionLog


class DeviceNetworkPolicy(Base):
    __tablename__ = "device_network_policies"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    device_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=False,
    )

    router_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("routers.id"),
        nullable=False,
    )

    requested_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("app_users.id"),
        nullable=False,
    )

    policy_type: Mapped[str] = mapped_column(String, nullable=False)

    bandwidth_limit_mbps: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    priority_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

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

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="network_policies",
    )

    router: Mapped["Router"] = relationship(
        "Router",
        back_populates="network_policies",
    )

    requested_by_user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="requested_device_network_policies",
    )

    router_action_logs: Mapped[list["RouterActionLog"]] = relationship(
        "RouterActionLog",
        back_populates="policy",
    )