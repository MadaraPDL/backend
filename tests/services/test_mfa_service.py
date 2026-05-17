from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import app.services.mfa_service as mfa_service


def test_mfa_challenge_is_inactive_after_five_attempts():
    challenge = SimpleNamespace(
        used_at=None,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        attempt_count=5,
    )

    assert mfa_service.is_mfa_challenge_active(challenge) is False
