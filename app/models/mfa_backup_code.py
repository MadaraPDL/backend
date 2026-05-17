from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.app_user import AppUser


class MFABackupCode(Base):
    __tablename__ = "mfa_backup_codes"

    __table_args__ = (
        Index("ix_mfa_backup_codes_admin_id", "admin_id"),
        Index("ix_mfa_backup_codes_app_user_id", "app_user_id"),
        Index(
            "ix_mfa_backup_codes_active_admin",
            "admin_id",
            postgresql_where=text("admin_id IS NOT NULL AND used_at IS NULL AND revoked_at IS NULL"),
        ),
        Index(
            "ix_mfa_backup_codes_active_app_user",
            "app_user_id",
            postgresql_where=text("app_user_id IS NOT NULL AND used_at IS NULL AND revoked_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    account_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    admin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=True,
    )

    app_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=True,
    )

    code_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    used_at: Mapped[datetime | None] = mapped_column(
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

    admin: Mapped["Admin | None"] = relationship(
        "Admin",
        back_populates="mfa_backup_codes",
    )

    app_user: Mapped["AppUser | None"] = relationship(
        "AppUser",
        back_populates="mfa_backup_codes",
    )
