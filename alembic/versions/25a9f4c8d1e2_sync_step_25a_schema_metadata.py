"""sync step 25a schema metadata

Revision ID: 25a9f4c8d1e2
Revises: 9d3aad01ea4e
Create Date: 2026-05-17

"""
from __future__ import annotations

from collections.abc import Iterable

from alembic import op


revision = "25a9f4c8d1e2"
down_revision = "9d3aad01ea4e"
branch_labels = None
depends_on = None


def _create_index(sql: str) -> None:
    op.execute(sql)


def _drop_index(name: str) -> None:
    op.execute(f"DROP INDEX IF EXISTS {name}")


def _drop_fk(table: str, name: str) -> None:
    op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}")


def _add_fk(
    table: str,
    name: str,
    columns: Iterable[str],
    referenced_table: str,
    referenced_columns: Iterable[str],
    ondelete: str | None = None,
) -> None:
    column_sql = ", ".join(columns)
    referenced_column_sql = ", ".join(referenced_columns)
    ondelete_sql = f" ON DELETE {ondelete}" if ondelete else ""

    op.execute(
        f"ALTER TABLE {table} "
        f"ADD CONSTRAINT {name} "
        f"FOREIGN KEY ({column_sql}) "
        f"REFERENCES {referenced_table} ({referenced_column_sql})"
        f"{ondelete_sql}"
    )


def _set_fk(
    table: str,
    name: str,
    columns: Iterable[str],
    referenced_table: str,
    referenced_columns: Iterable[str],
    ondelete: str | None = None,
) -> None:
    _drop_fk(table, name)
    _add_fk(table, name, columns, referenced_table, referenced_columns, ondelete)


def _upgrade_indexes() -> None:
    _create_index("CREATE INDEX IF NOT EXISTS ix_account_invitations_email ON account_invitations (lower(email))")
    _create_index("CREATE INDEX IF NOT EXISTS ix_account_invitations_expires_at ON account_invitations (expires_at)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_account_invitations_token_hash ON account_invitations (token_hash)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_admins_isp_id ON admins (isp_id)")
    _create_index("CREATE UNIQUE INDEX IF NOT EXISTS ux_admins_username_lower ON admins (lower(username)) WHERE username IS NOT NULL")

    _create_index("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts (user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_alerts_user_subscription_id ON alerts (user_subscription_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_app_users_isp_id ON app_users (isp_id)")
    _create_index("CREATE UNIQUE INDEX IF NOT EXISTS ux_app_users_username_lower ON app_users (lower(username)) WHERE username IS NOT NULL")

    _create_index("CREATE INDEX IF NOT EXISTS idx_device_connection_logs_device_id ON device_connection_logs (device_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_device_connection_logs_router_id ON device_connection_logs (router_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_device_network_policies_device_id ON device_network_policies (device_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_device_network_policies_router_id ON device_network_policies (router_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_devices_router_id ON devices (router_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices (user_id)")

    _create_index("CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_admin_id ON email_verification_tokens (admin_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_app_user_id ON email_verification_tokens (app_user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_token_hash ON email_verification_tokens (token_hash)")

    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_backup_codes_admin_id ON mfa_backup_codes (admin_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_backup_codes_app_user_id ON mfa_backup_codes (app_user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_backup_codes_active_admin ON mfa_backup_codes (admin_id) WHERE admin_id IS NOT NULL AND used_at IS NULL AND revoked_at IS NULL")
    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_backup_codes_active_app_user ON mfa_backup_codes (app_user_id) WHERE app_user_id IS NOT NULL AND used_at IS NULL AND revoked_at IS NULL")

    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_setup_challenges_revoked_at ON mfa_setup_challenges (revoked_at)")

    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_challenges_admin_id ON mfa_challenges (admin_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_challenges_app_user_id ON mfa_challenges (app_user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_challenges_expires_at ON mfa_challenges (expires_at)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_mfa_challenges_token_hash ON mfa_challenges (challenge_token_hash)")

    _create_index("CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_admin_id ON password_reset_tokens (admin_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_app_user_id ON password_reset_tokens (app_user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_expires_at ON password_reset_tokens (expires_at)")
    _create_index("CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions (user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_predictions_user_subscription_id ON predictions (user_subscription_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations (user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_recommendations_user_subscription_id ON recommendations (user_subscription_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_reports_isp_id ON reports (isp_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_router_action_logs_policy_id ON router_action_logs (policy_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_router_action_logs_router_id ON router_action_logs (router_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_routers_isp_id ON routers (isp_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_routers_user_subscription_id ON routers (user_subscription_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_subscription_change_requests_reviewed_by_admin_id ON subscription_change_requests (reviewed_by_admin_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_subscription_change_requests_status ON subscription_change_requests (status)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_subscription_change_requests_user_id ON subscription_change_requests (user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_subscription_change_requests_user_subscription_id ON subscription_change_requests (user_subscription_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_subscription_plans_isp_id ON subscription_plans (isp_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_usage_records_device_id ON usage_records (device_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_usage_records_record_start ON usage_records (record_start)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_usage_records_router_id ON usage_records (router_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_usage_records_user_id ON usage_records (user_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_usage_records_user_subscription_id ON usage_records (user_subscription_id)")

    _create_index("CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON user_subscriptions (plan_id)")
    _create_index("CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions (user_id)")


def _upgrade_foreign_keys() -> None:
    _set_fk("admins", "admins_isp_id_fkey", ["isp_id"], "isps", ["id"], "SET NULL")
    _set_fk("admins", "admins_created_by_admin_id_fkey", ["created_by_admin_id"], "admins", ["id"], "SET NULL")

    _set_fk("alerts", "alerts_device_id_fkey", ["device_id"], "devices", ["id"], "SET NULL")
    _set_fk("alerts", "alerts_usage_id_fkey", ["usage_id"], "usage_records", ["id"], "SET NULL")
    _set_fk("alerts", "alerts_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")
    _set_fk("alerts", "alerts_connection_log_id_fkey", ["connection_log_id"], "device_connection_logs", ["id"], "SET NULL")
    _set_fk("alerts", "alerts_prediction_id_fkey", ["prediction_id"], "predictions", ["id"], "SET NULL")
    _set_fk("alerts", "alerts_user_subscription_id_fkey", ["user_subscription_id"], "user_subscriptions", ["id"], "SET NULL")

    _set_fk("app_users", "app_users_isp_id_fkey", ["isp_id"], "isps", ["id"], "CASCADE")
    _set_fk("app_users", "app_users_created_by_admin_id_fkey", ["created_by_admin_id"], "admins", ["id"], "SET NULL")

    _set_fk("device_connection_logs", "device_connection_logs_router_id_fkey", ["router_id"], "routers", ["id"], "CASCADE")
    _set_fk("device_connection_logs", "device_connection_logs_device_id_fkey", ["device_id"], "devices", ["id"], "CASCADE")

    _set_fk("device_network_policies", "device_network_policies_device_id_fkey", ["device_id"], "devices", ["id"], "CASCADE")
    _set_fk("device_network_policies", "device_network_policies_router_id_fkey", ["router_id"], "routers", ["id"], "CASCADE")
    _set_fk("device_network_policies", "device_network_policies_requested_by_user_id_fkey", ["requested_by_user_id"], "app_users", ["id"], "CASCADE")

    _set_fk("devices", "devices_router_id_fkey", ["router_id"], "routers", ["id"], "CASCADE")
    _set_fk("devices", "devices_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")

    _drop_fk("isps", "fk_isps_created_by_admin")
    _set_fk("isps", "fk_isps_created_by_admin_id", ["created_by_admin_id"], "admins", ["id"], "SET NULL")

    _set_fk("predictions", "predictions_plan_id_fkey", ["plan_id"], "subscription_plans", ["id"], "SET NULL")
    _set_fk("predictions", "predictions_user_subscription_id_fkey", ["user_subscription_id"], "user_subscriptions", ["id"], "CASCADE")
    _set_fk("predictions", "predictions_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")

    _set_fk("recommendations", "recommendations_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")
    _set_fk("recommendations", "recommendations_prediction_id_fkey", ["prediction_id"], "predictions", ["id"], "SET NULL")
    _set_fk("recommendations", "recommendations_current_plan_id_fkey", ["current_plan_id"], "subscription_plans", ["id"], "SET NULL")
    _set_fk("recommendations", "recommendations_recommendation_plan_id_fkey", ["recommendation_plan_id"], "subscription_plans", ["id"], "SET NULL")
    _set_fk("recommendations", "recommendations_user_subscription_id_fkey", ["user_subscription_id"], "user_subscriptions", ["id"], "CASCADE")

    _set_fk("reports", "reports_generated_by_admin_id_fkey", ["generated_by_admin_id"], "admins", ["id"], "SET NULL")
    _set_fk("reports", "reports_isp_id_fkey", ["isp_id"], "isps", ["id"], "CASCADE")

    _set_fk("router_action_logs", "router_action_logs_policy_id_fkey", ["policy_id"], "device_network_policies", ["id"], "SET NULL")
    _set_fk("router_action_logs", "router_action_logs_router_id_fkey", ["router_id"], "routers", ["id"], "CASCADE")

    _set_fk("routers", "routers_user_subscription_id_fkey", ["user_subscription_id"], "user_subscriptions", ["id"], "SET NULL")
    _set_fk("routers", "routers_assigned_by_admin_id_fkey", ["assigned_by_admin_id"], "admins", ["id"], "SET NULL")
    _set_fk("routers", "routers_isp_id_fkey", ["isp_id"], "isps", ["id"], "CASCADE")

    _set_fk("subscription_change_requests", "subscription_change_requests_reviewed_by_admin_id_fkey", ["reviewed_by_admin_id"], "admins", ["id"], "SET NULL")
    _set_fk("subscription_change_requests", "subscription_change_requests_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")
    _set_fk("subscription_change_requests", "subscription_change_requests_requested_plan_id_fkey", ["requested_plan_id"], "subscription_plans", ["id"], "RESTRICT")
    _set_fk("subscription_change_requests", "subscription_change_requests_recommendation_id_fkey", ["recommendation_id"], "recommendations", ["id"], "SET NULL")
    _set_fk("subscription_change_requests", "subscription_change_requests_current_plan_id_fkey", ["current_plan_id"], "subscription_plans", ["id"], "RESTRICT")
    _set_fk("subscription_change_requests", "subscription_change_requests_user_subscription_id_fkey", ["user_subscription_id"], "user_subscriptions", ["id"], "CASCADE")

    _set_fk("subscription_plans", "subscription_plans_isp_id_fkey", ["isp_id"], "isps", ["id"], "CASCADE")
    _set_fk("subscription_plans", "subscription_plans_created_by_admin_id_fkey", ["created_by_admin_id"], "admins", ["id"], "SET NULL")

    _set_fk("usage_records", "usage_records_device_id_fkey", ["device_id"], "devices", ["id"], "SET NULL")
    _set_fk("usage_records", "usage_records_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")
    _set_fk("usage_records", "usage_records_user_subscription_id_fkey", ["user_subscription_id"], "user_subscriptions", ["id"], "CASCADE")
    _set_fk("usage_records", "usage_records_router_id_fkey", ["router_id"], "routers", ["id"], "CASCADE")

    _set_fk("user_subscriptions", "user_subscriptions_user_id_fkey", ["user_id"], "app_users", ["id"], "CASCADE")
    _set_fk("user_subscriptions", "user_subscriptions_plan_id_fkey", ["plan_id"], "subscription_plans", ["id"], "RESTRICT")
    _set_fk("user_subscriptions", "user_subscriptions_assigned_by_admin_id_fkey", ["assigned_by_admin_id"], "admins", ["id"], "SET NULL")


def upgrade() -> None:
    _upgrade_indexes()
    _upgrade_foreign_keys()


def downgrade() -> None:
    for index_name in [
        "ix_account_invitations_email",
        "ix_account_invitations_expires_at",
        "ix_account_invitations_token_hash",
        "idx_admins_isp_id",
        "ux_admins_username_lower",
        "idx_alerts_status",
        "idx_alerts_user_id",
        "idx_alerts_user_subscription_id",
        "idx_app_users_isp_id",
        "ux_app_users_username_lower",
        "idx_device_connection_logs_device_id",
        "idx_device_connection_logs_router_id",
        "idx_device_network_policies_device_id",
        "idx_device_network_policies_router_id",
        "idx_devices_router_id",
        "idx_devices_user_id",
        "ix_email_verification_tokens_admin_id",
        "ix_email_verification_tokens_app_user_id",
        "ix_email_verification_tokens_token_hash",
        "ix_mfa_backup_codes_admin_id",
        "ix_mfa_backup_codes_app_user_id",
        "ix_mfa_backup_codes_active_admin",
        "ix_mfa_backup_codes_active_app_user",
        "ix_mfa_setup_challenges_revoked_at",
        "ix_mfa_challenges_admin_id",
        "ix_mfa_challenges_app_user_id",
        "ix_mfa_challenges_expires_at",
        "ix_mfa_challenges_token_hash",
        "ix_password_reset_tokens_admin_id",
        "ix_password_reset_tokens_app_user_id",
        "ix_password_reset_tokens_expires_at",
        "ix_password_reset_tokens_token_hash",
        "idx_predictions_user_id",
        "idx_predictions_user_subscription_id",
        "idx_recommendations_user_id",
        "idx_recommendations_user_subscription_id",
        "idx_reports_isp_id",
        "idx_router_action_logs_policy_id",
        "idx_router_action_logs_router_id",
        "idx_routers_isp_id",
        "idx_routers_user_subscription_id",
        "idx_subscription_change_requests_reviewed_by_admin_id",
        "idx_subscription_change_requests_status",
        "idx_subscription_change_requests_user_id",
        "idx_subscription_change_requests_user_subscription_id",
        "idx_subscription_plans_isp_id",
        "idx_usage_records_device_id",
        "idx_usage_records_record_start",
        "idx_usage_records_router_id",
        "idx_usage_records_user_id",
        "idx_usage_records_user_subscription_id",
        "idx_user_subscriptions_plan_id",
        "idx_user_subscriptions_user_id",
    ]:
        _drop_index(index_name)
