from __future__ import annotations

from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.device import Device
    from app.models.router import Router


class DeviceConnectionLog(Base):
    __tablename__ = "device_connection_logs"

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

    event_type: Mapped[str] = mapped_column(String, nullable=False)

    ip_address: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET,
        nullable=True,
    )

    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    device: Mapped["Device"] = relationship(
        "Device",
        back_populates="connection_logs",
    )

    router: Mapped["Router"] = relationship(
        "Router",
        back_populates="connection_logs",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="connection_log",
    )