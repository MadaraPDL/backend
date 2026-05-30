from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

EXPO_PUSH_SEND_URL = "https://exp.host/--/api/v2/push/send"
MAX_EXPO_MESSAGES_PER_REQUEST = 100


@dataclass(frozen=True)
class ExpoPushMessage:
    to: str
    title: str
    body: str
    data: dict[str, Any] | None = None
    sound: str | None = "default"
    priority: str = "default"
    channel_id: str | None = "pulsefi-alerts"


@dataclass(frozen=True)
class ExpoPushSendResult:
    attempted: int
    accepted: int
    failed: int
    tickets: list[dict[str, Any]]
    errors: list[str]


def is_valid_expo_push_token(token: str) -> bool:
    return token.startswith("ExpoPushToken[") or token.startswith("ExponentPushToken[")


def sanitize_notification_text(value: str, *, max_length: int) -> str:
    cleaned = " ".join(value.strip().split())

    if len(cleaned) <= max_length:
        return cleaned

    return cleaned[: max_length - 1].rstrip() + "…"


def build_expo_payload(message: ExpoPushMessage) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "to": message.to,
        "title": sanitize_notification_text(message.title, max_length=80),
        "body": sanitize_notification_text(message.body, max_length=160),
        "priority": message.priority,
    }

    if message.sound:
        payload["sound"] = message.sound

    if message.channel_id:
        payload["channelId"] = message.channel_id

    if message.data:
        payload["data"] = message.data

    return payload


def chunk_messages(messages: list[ExpoPushMessage]) -> list[list[ExpoPushMessage]]:
    return [
        messages[index : index + MAX_EXPO_MESSAGES_PER_REQUEST]
        for index in range(0, len(messages), MAX_EXPO_MESSAGES_PER_REQUEST)
    ]


async def send_expo_push_notifications(
    messages: list[ExpoPushMessage],
    *,
    timeout_seconds: float = 10.0,
) -> ExpoPushSendResult:
    valid_messages = [
        message
        for message in messages
        if is_valid_expo_push_token(message.to)
    ]

    if not valid_messages:
        return ExpoPushSendResult(
            attempted=0,
            accepted=0,
            failed=0,
            tickets=[],
            errors=[],
        )

    tickets: list[dict[str, Any]] = []
    errors: list[str] = []
    accepted = 0
    failed = 0

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        for message_chunk in chunk_messages(valid_messages):
            payload = [build_expo_payload(message) for message in message_chunk]

            try:
                response = await client.post(
                    EXPO_PUSH_SEND_URL,
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                response_payload = response.json()
            except Exception as exc:
                failed += len(message_chunk)
                errors.append(str(exc))
                continue

            raw_tickets = response_payload.get("data", [])

            if isinstance(raw_tickets, dict):
                raw_tickets = [raw_tickets]

            if not isinstance(raw_tickets, list):
                failed += len(message_chunk)
                errors.append("Expo push response did not include ticket data.")
                continue

            for ticket in raw_tickets:
                if not isinstance(ticket, dict):
                    failed += 1
                    errors.append("Expo push ticket was not an object.")
                    continue

                tickets.append(ticket)

                if ticket.get("status") == "ok":
                    accepted += 1
                else:
                    failed += 1

                    message = ticket.get("message")
                    details = ticket.get("details")

                    if isinstance(message, str):
                        errors.append(message)
                    elif isinstance(details, dict):
                        errors.append(str(details))
                    else:
                        errors.append("Expo push ticket returned an error.")

    return ExpoPushSendResult(
        attempted=len(valid_messages),
        accepted=accepted,
        failed=failed,
        tickets=tickets,
        errors=errors,
    )
