from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.app_user import plan_change_requests as endpoint_module
from app.schemas.app_user import MyPlanChangeRequestCreate
from app.services.app_user.plan_change_request_service import (
    PlanChangeRequestValidationError,
)


@pytest.mark.asyncio
async def test_plan_change_request_returns_specific_validation_detail(monkeypatch):
    expected_message = (
        "A pending plan upgrade request already exists for this service line."
    )

    async def fake_create_my_plan_change_request(**kwargs):
        raise PlanChangeRequestValidationError(expected_message)

    monkeypatch.setattr(
        endpoint_module,
        "create_my_plan_change_request",
        fake_create_my_plan_change_request,
    )

    request = MyPlanChangeRequestCreate(
        user_subscription_id=uuid4(),
        requested_plan_id=uuid4(),
        request_type="upgrade",
        confirmation_text="CHANGE PLAN",
        reason="Need a higher data bundle.",
    )

    with pytest.raises(HTTPException) as exc_info:
        await endpoint_module.create_my_plan_change_request_endpoint(
            data=request,
            db=object(),
            current_user=object(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == expected_message
