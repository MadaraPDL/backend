from app.maintenance.cleanup_mfa_setup_challenges import build_parser
from app.services.mfa_setup_cleanup_service import (
    DEFAULT_MFA_SETUP_CLEANUP_RETENTION_DAYS,
)


def test_cleanup_mfa_setup_challenges_parser_uses_default_retention():
    args = build_parser().parse_args([])

    assert args.retention_days == DEFAULT_MFA_SETUP_CLEANUP_RETENTION_DAYS


def test_cleanup_mfa_setup_challenges_parser_accepts_custom_retention():
    args = build_parser().parse_args(["--retention-days", "3"])

    assert args.retention_days == 3
