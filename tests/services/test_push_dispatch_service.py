from uuid import uuid4

from app.models.recommendation import Recommendation
from app.services.notifications.push_dispatch_service import (
    build_push_messages_for_user,
    empty_push_result,
    should_notify_recommendation,
)


def test_empty_push_result_has_zero_counts() -> None:
    result = empty_push_result()

    assert result.attempted == 0
    assert result.accepted == 0
    assert result.failed == 0
    assert result.tickets == []
    assert result.errors == []


def test_build_push_messages_for_user_uses_generic_payload() -> None:
    messages = build_push_messages_for_user(
        expo_push_tokens=[
            "ExpoPushToken[token-a]",
            "ExpoPushToken[token-b]",
        ],
        title="PulseFi recommendation update",
        body="Open PulseFi to review your latest plan recommendation.",
        data={
            "screen": "More",
            "section": "insights",
        },
    )

    assert len(messages) == 2
    assert messages[0].to == "ExpoPushToken[token-a]"
    assert messages[1].to == "ExpoPushToken[token-b]"
    assert messages[0].title == "PulseFi recommendation update"
    assert messages[0].body == "Open PulseFi to review your latest plan recommendation."
    assert messages[0].data == {
        "screen": "More",
        "section": "insights",
    }


def test_should_notify_recommendation_skips_stay_current() -> None:
    recommendation = Recommendation(
        user_id=uuid4(),
        user_subscription_id=uuid4(),
        current_plan_id=uuid4(),
        recommendation_plan_id=None,
        prediction_id=uuid4(),
        recommendation_type="stay_current",
        recommendation_text="Stay on your current plan.",
        reason="Current plan is suitable.",
        confidence_score=90,
        status="new",
    )

    assert should_notify_recommendation(recommendation) is False


def test_should_notify_recommendation_allows_meaningful_plan_changes() -> None:
    recommendation = Recommendation(
        user_id=uuid4(),
        user_subscription_id=uuid4(),
        current_plan_id=uuid4(),
        recommendation_plan_id=uuid4(),
        prediction_id=uuid4(),
        recommendation_type="upgrade_plan",
        recommendation_text="Upgrade recommended.",
        reason="Predicted high usage.",
        confidence_score=90,
        status="new",
    )

    assert should_notify_recommendation(recommendation) is True
