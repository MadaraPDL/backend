from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ISPStatus= Literal["active", "inactive", "suspended"]

class ISPCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    contact_email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=50)
    address: str | None = None


class ISPUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    contact_email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=50)
    address: str | None = None
    status: ISPStatus | None = None


class ISPResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    contact_email: EmailStr | None
    phone_number: str | None
    address: str | None
    status: str
    created_by_admin_id: UUID | None
    created_at: datetime
    updated_at: datetime