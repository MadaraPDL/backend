from __future__ import annotations

from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.device_network_policy import DeviceNetworkPolicy
    from app.models.usage_record import UsageRecord
    from app.models.user_subscription import UserSubscription
    from app.models.device import Device
    from app.models.device_connection_log import DeviceConnectionLog
    from app.models.router_action_log import RouterActionLog
    from app.models.isp import ISP




class Router(Base):
    __tablename__ = "routers"

    __table_args__ = (
        Index("idx_routers_isp_id", "isp_id"),
        Index("idx_routers_user_subscription_id", "user_subscription_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    isp_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("isps.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_subscription_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_subscriptions.id", ondelete="SET NULL"),
        nullable=True,
    )

    assigned_by_admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )

    router_name: Mapped[str | None] = mapped_column(String, nullable=True)
    router_model: Mapped[str | None] = mapped_column(String, nullable=True)

    router_ip: Mapped[IPv4Address | IPv6Address | None] = mapped_column(
        INET,
        nullable=True,
    )

    mac_address: Mapped[str | None] = mapped_column(String, nullable=True)
    api_endpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'active'"),
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
        back_populates="routers",
    )

    user_subscription: Mapped["UserSubscription | None"] = relationship(
        "UserSubscription",
        back_populates="routers",
    )

    assigned_by_admin: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="assigned_routers",
    )

    devices: Mapped[list["Device"]] = relationship(
        "Device",
        back_populates="router",
    )

    connection_logs: Mapped[list["DeviceConnectionLog"]] = relationship(
        "DeviceConnectionLog",
        back_populates="router",
    )

    usage_records: Mapped[list["UsageRecord"]] = relationship(
        "UsageRecord",
        back_populates="router",
    )

    network_policies: Mapped[list["DeviceNetworkPolicy"]] = relationship(
        "DeviceNetworkPolicy",
        back_populates="router",
    )

    router_action_logs: Mapped[list["RouterActionLog"]] = relationship(
        "RouterActionLog",
        back_populates="router",
    )
