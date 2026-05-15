from app.services.mfa_setup_token_service import (
    generate_mfa_setup_token,
    hash_mfa_setup_token,
)


def test_generate_mfa_setup_token_returns_raw_token_and_hash():
    raw_token, token_hash = generate_mfa_setup_token()

    assert raw_token
    assert token_hash
    assert raw_token != token_hash


def test_hash_mfa_setup_token_is_stable():
    raw_token, token_hash = generate_mfa_setup_token()

    assert hash_mfa_setup_token(raw_token) == token_hash


def test_different_setup_tokens_have_different_hashes():
    first_raw_token, first_hash = generate_mfa_setup_token()
    second_raw_token, second_hash = generate_mfa_setup_token()

    assert first_raw_token != second_raw_token
    assert first_hash != second_hash
