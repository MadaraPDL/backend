import pytest

from app.services.notifications.expo_push_service import (
    ExpoPushMessage,
    build_expo_payload,
    chunk_messages,
    is_valid_expo_push_token,
    sanitize_notification_text,
    send_expo_push_notifications,
)


def test_is_valid_expo_push_token_accepts_expo_formats() -> None:
    assert is_valid_expo_push_token("ExpoPushToken[abc123]")
    assert is_valid_expo_push_token("ExponentPushToken[abc123]")


def test_is_valid_expo_push_token_rejects_invalid_formats() -> None:
    assert not is_valid_expo_push_token("invalid")
    assert not is_valid_expo_push_token("")
    assert not is_valid_expo_push_token("Bearer abc")


def test_sanitize_notification_text_collapses_whitespace_and_truncates() -> None:
    text = "  High   usage\n\nalert   " + ("x" * 200)

    result = sanitize_notification_text(text, max_length=40)

    assert "\n" not in result
    assert "  " not in result
    assert len(result) <= 40
    assert result.endswith("…")


def test_build_expo_payload_uses_safe_fields() -> None:
    payload = build_expo_payload(
        ExpoPushMessage(
            to="ExpoPushToken[abc123]",
            title="PulseFi Alert",
            body="High usage detected.",
            data={"screen": "Alerts", "type": "high_usage"},
        )
    )

    assert payload["to"] == "ExpoPushToken[abc123]"
    assert payload["title"] == "PulseFi Alert"
    assert payload["body"] == "High usage detected."
    assert payload["channelId"] == "pulsefi-alerts"
    assert payload["data"] == {"screen": "Alerts", "type": "high_usage"}


def test_chunk_messages_limits_expo_request_size() -> None:
    messages = [
        ExpoPushMessage(
            to=f"ExpoPushToken[token-{index}]",
            title="PulseFi",
            body="Test",
        )
        for index in range(205)
    ]

    chunks = chunk_messages(messages)

    assert [len(chunk) for chunk in chunks] == [100, 100, 5]


@pytest.mark.asyncio
async def test_send_expo_push_notifications_skips_invalid_tokens() -> None:
    result = await send_expo_push_notifications(
        [
            ExpoPushMessage(
                to="not-a-token",
                title="PulseFi",
                body="Invalid token should be skipped.",
            )
        ]
    )

    assert result.attempted == 0
    assert result.accepted == 0
    assert result.failed == 0
    assert result.tickets == []
    assert result.errors == []
