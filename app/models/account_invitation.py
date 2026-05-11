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
    from app.models.isp import ISP


class AccountInvitation(Base):
    __tablename__ = "account_invitations"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    account_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    admin_role: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    isp_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("isps.id", ondelete="SET NULL"),
        nullable=True,
    )

    invited_by_admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )

    token_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    isp: Mapped["ISP | None"] = relationship(
        "ISP",
    )

    invited_by_admin: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="sent_account_invitations",
    )