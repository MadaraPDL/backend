from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.device_network_policy import DeviceNetworkPolicy
    from app.models.router import Router


class RouterActionLog(Base):
    __tablename__ = "router_action_logs"

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

    policy_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("device_network_policies.id"),
        nullable=True,
    )

    action_type: Mapped[str] = mapped_column(String, nullable=False)

    command_payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    response_payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=text("'pending'"),
    )

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    router: Mapped["Router"] = relationship(
        "Router",
        back_populates="router_action_logs",
    )

    policy: Mapped["DeviceNetworkPolicy | None"] = relationship(
        "DeviceNetworkPolicy",
        back_populates="router_action_logs",
    )