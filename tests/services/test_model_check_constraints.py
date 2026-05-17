from sqlalchemy import CheckConstraint

from app.models.device_network_policy import DeviceNetworkPolicy
from app.models.recommendation import Recommendation
from app.models.report import Report
from app.models.user_subscription import UserSubscription


def _check_constraint_names(model) -> set[str]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }


def test_step_26_quality_check_constraints_are_registered_on_models():
    assert {
        "chk_device_network_policy_type",
        "chk_device_network_policy_status",
    }.issubset(_check_constraint_names(DeviceNetworkPolicy))

    assert {
        "chk_recommendation_type",
        "chk_recommendation_status",
    }.issubset(_check_constraint_names(Recommendation))

    assert "chk_report_type" in _check_constraint_names(Report)
    assert "chk_user_subscription_status" in _check_constraint_names(UserSubscription)
