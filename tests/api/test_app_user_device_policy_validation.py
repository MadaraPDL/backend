from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.api.dependencies import get_current_app_user
from app.main import app
from app.schemas.app_user.device_policies import MyDevicePolicyCreate


def test_bandwidth_limit_policy_requires_bandwidth_limit() -> None:
    with pytest.raises(ValidationError):
        MyDevicePolicyCreate(
            device_id=uuid4(),
            policy_type="bandwidth_limit",
        )


def test_bandwidth_limit_policy_rejects_priority_level() -> None:
    with pytest.raises(ValidationError):
        MyDevicePolicyCreate(
            device_id=uuid4(),
            policy_type="bandwidth_limit",
            bandwidth_limit_mbps=25,
            priority_level=5,
        )


def test_device_priority_policy_requires_priority_level() -> None:
    with pytest.raises(ValidationError):
        MyDevicePolicyCreate(
            device_id=uuid4(),
            policy_type="device_priority",
        )


def test_device_priority_policy_rejects_bandwidth_limit() -> None:
    with pytest.raises(ValidationError):
        MyDevicePolicyCreate(
            device_id=uuid4(),
            policy_type="device_priority",
            priority_level=5,
            bandwidth_limit_mbps=25,
        )


def test_invalid_policy_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        MyDevicePolicyCreate(
            device_id=uuid4(),
            policy_type="unsupported_policy",
        )


def test_valid_bandwidth_limit_policy_is_accepted() -> None:
    policy = MyDevicePolicyCreate(
        device_id=uuid4(),
        policy_type="bandwidth_limit",
        bandwidth_limit_mbps=25,
    )

    assert policy.policy_type == "bandwidth_limit"
    assert policy.bandwidth_limit_mbps == 25
    assert policy.priority_level is None


def test_valid_device_priority_policy_is_accepted() -> None:
    policy = MyDevicePolicyCreate(
        device_id=uuid4(),
        policy_type="device_priority",
        priority_level=5,
    )

    assert policy.policy_type == "device_priority"
    assert policy.priority_level == 5
    assert policy.bandwidth_limit_mbps is None


def test_device_policy_api_returns_standard_validation_error(api_client):
    async def override_current_user():
        return object()

    app.dependency_overrides[get_current_app_user] = override_current_user

    response = api_client.post(
        "/api/v1/me/device-policies",
        json={
            "device_id": str(uuid4()),
            "policy_type": "unsupported_policy",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert isinstance(body["details"], list)
