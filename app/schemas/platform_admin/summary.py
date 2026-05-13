from __future__ import annotations

from pydantic import BaseModel


class PlatformAdminSummaryResponse(BaseModel):
    total_isps: int
    active_isps: int
    inactive_isps: int
    suspended_isps: int

    total_isp_admins: int
    active_isp_admins: int
    inactive_isp_admins: int
    suspended_isp_admins: int

    total_app_users: int
    active_app_users: int
    inactive_app_users: int
    suspended_app_users: int
