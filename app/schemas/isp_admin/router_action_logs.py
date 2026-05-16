from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


RouterActionLogStatus = Literal[
    "pending",
    "success",
    "failed",
]


class RouterActionLogResponse(BaseModel):
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
