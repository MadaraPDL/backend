from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


DevicePolicyType = Literal["bandwidth_limit", "device_priority"]


class MyDevicePolicyCreate(BaseModel):
    device_id: UUID
    policy_type: DevicePolicyType
    bandwidth_limit_mbps: Decimal | None = Field(default=None, gt=0)
    download_limit_mbps: Decimal | None = Field(default=None, gt=0)
    upload_limit_mbps: Decimal | None = Field(default=None, gt=0)
    priority_level: int | None = Field(default=None, ge=1, le=10)

    @model_validator(mode="after")
    def validate_action_fields(self) -> "MyDevicePolicyCreate":
        if self.policy_type == "bandwidth_limit":
            has_any_bandwidth_limit = any(
                value is not None
                for value in (
                    self.bandwidth_limit_mbps,
                    self.download_limit_mbps,
                    self.upload_limit_mbps,
                )
            )

            if not has_any_bandwidth_limit:
                raise ValueError(
                    "bandwidth_limit policies require at least one bandwidth limit."
                )

            if self.priority_level is not None:
                raise ValueError("bandwidth_limit policies must not include priority_level.")

        if self.policy_type == "device_priority":
            if self.priority_level is None:
                raise ValueError("device_priority policies require priority_level.")

            if any(
                value is not None
                for value in (
                    self.bandwidth_limit_mbps,
                    self.download_limit_mbps,
                    self.upload_limit_mbps,
                )
            ):
                raise ValueError("device_priority policies must not include bandwidth limits.")

        return self


class MyDevicePolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    router_id: UUID
    policy_type: str
    bandwidth_limit_mbps: Decimal | None
    download_limit_mbps: Decimal | None
    upload_limit_mbps: Decimal | None
    priority_level: int | None
    status: str
    requested_at: datetime
    applied_at: datetime | None
    failure_reason: str | None
    is_active: bool
    updated_at: datetime


class MyRouterActionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    router_id: UUID
    policy_id: UUID | None
    action_type: str
    command_payload: dict | None
    response_payload: dict | None
    status: str
    error_message: str | None
    executed_at: datetime


class MyDevicePolicyExecutionResponse(BaseModel):
    policy: MyDevicePolicyResponse
    action_log: MyRouterActionLogResponse | None
    message: str
