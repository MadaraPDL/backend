from datetime import timedelta
from uuid import uuid4

import jwt

from app.core.config import settings
from app.core.security import create_access_token
from app.services.mfa_setup_token_service import (
    MFA_SETUP_TOKEN_AUDIENCE,
    MFA_SETUP_TOKEN_TYPE,
    create_mfa_setup_token,
    decode_mfa_setup_token,
)


def test_mfa_setup_token_round_trip():
    account_id = uuid4()

    token = create_mfa_setup_token(
        subject=account_id,
        setup_account_type="admin",
        authenticator_secret="ABC123SECRET",
    )

    payload = decode_mfa_setup_token(token)

    assert payload is not None
    assert payload.account_id == account_id
    assert payload.account_type == "admin"
    assert payload.authenticator_secret == "ABC123SECRET"


def test_mfa_setup_decoder_rejects_normal_access_token():
    token = create_access_token(
        subject=uuid4(),
        account_type="admin",
    )

    assert decode_mfa_setup_token(token) is None


def test_mfa_setup_decoder_rejects_expired_setup_token():
    token = create_mfa_setup_token(
        subject=uuid4(),
        setup_account_type="admin",
        authenticator_secret="ABC123SECRET",
        expires_delta=timedelta(seconds=-1),
    )

    assert decode_mfa_setup_token(token) is None


def test_mfa_setup_decoder_rejects_wrong_purpose():
    now_payload = {
        "sub": str(uuid4()),
        "setup_account_type": "admin",
        "purpose": "wrong_purpose",
        "token_type": MFA_SETUP_TOKEN_TYPE,
        "authenticator_secret": "ABC123SECRET",
        "aud": MFA_SETUP_TOKEN_AUDIENCE,
        "iss": settings.APP_NAME,
        "jti": "test-jti",
    }

    token = jwt.encode(
        now_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    assert decode_mfa_setup_token(token) is None
