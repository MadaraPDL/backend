from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


RouterStatus = Literal[
    "active",
    "inactive",
    "maintenance",
]


class RouterCreateRequest(BaseModel):
    user_subscription_id: UUID
    router_name: str | None = Field(default=None, min_length=2, max_length=120)
    router_model: str | None = Field(default=None, max_length=120)
    router_ip: IPvAnyAddress | None = None
    mac_address: str | None = Field(default=None, max_length=50)
    api_endpoint: str | None = Field(default=None, max_length=1000)
    username: str | None = Field(default=None, max_length=120)
    status: RouterStatus = "active"


class RouterUpdateRequest(BaseModel):
    user_subscription_id: UUID | None = None
    router_name: str | None = Field(default=None, min_length=2, max_length=120)
    router_model: str | None = Field(default=None, max_length=120)
    router_ip: IPvAnyAddress | None = None
    mac_address: str | None = Field(default=None, max_length=50)
    api_endpoint: str | None = Field(default=None, max_length=1000)
    username: str | None = Field(default=None, max_length=120)
    status: RouterStatus | None = None


class RouterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    isp_id: UUID
    user_subscription_id: UUID | None
    assigned_by_admin_id: UUID | None
    router_name: str | None
    router_model: str | None
    router_ip: IPvAnyAddress | None
    mac_address: str | None
    api_endpoint: str | None
    username: str | None
    status: str
    created_at: datetime
    updated_at: datetime
