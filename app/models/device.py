from __future__ import annotations

from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.usage_record import UsageRecord
    from app.models.device_network_policy import DeviceNetworkPolicy
    from app.models.alert import Alert
    from app.models.app_user import AppUser
    from app.models.router import Router
    from app.models.device_connection_log import DeviceConnectionLog

class Device(Base):
    __tablename__ = "devices"

    __table_args__ = (
        UniqueConstraint("router_id", "mac_address"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    router_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("routers.id"),
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("app_users.id"),
        nullable=False,
    )

    device_name: Mapped[str | None] = mapped_column(String, nullable=True)
    mac_address: Mapped[str] = mapped_column(String, nullable=False)

    ip_address: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET,
        nullable=True,
    )

    device_type: Mapped[str | None] = mapped_column(String, nullable=True)

    is_trusted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'connected'"),
    )

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    router: Mapped["Router"] = relationship(
        "Router",
        back_populates="devices",
    )

    user: Mapped["AppUser"] = relationship(
        "AppUser",
        back_populates="devices",
    )

    usage_records: Mapped[list["UsageRecord"]] = relationship(
        "UsageRecord",
        back_populates="device",
    )

    connection_logs: Mapped[list["DeviceConnectionLog"]] = relationship(
        "DeviceConnectionLog",
        back_populates="device",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="device",
    )

    network_policies: Mapped[list["DeviceNetworkPolicy"]] = relationship(
        "DeviceNetworkPolicy",
        back_populates="device",
    )