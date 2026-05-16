from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.alert import Alert
from app.models.app_user import AppUser
from app.models.device import Device
from app.models.recommendation import Recommendation
from app.models.report import Report
from app.models.router import Router
from app.models.router_action_log import RouterActionLog
from app.models.usage_record import UsageRecord
from app.schemas.isp_admin import ISPAdminReportCreateRequest
from app.services.isp_admin.analytics_service import get_isp_admin_analytics_summary


_REPORT_TITLES = {
    "usage_report": "Usage Report",
    "device_report": "Device Report",
    "alert_report": "Alert Report",
    "recommendation_report": "Recommendation Report",
    "network_performance_report": "Network Performance Report",
}


def _period_start_to_datetime(value: date | None) -> datetime | None:
    if value is None:
        return None

    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _period_end_to_datetime(value: date | None) -> datetime | None:
    if value is None:
        return None

    return datetime.combine(value, time.max, tzinfo=timezone.utc)


def _apply_period_filter(stmt, column, period_start: datetime | None, period_end: datetime | None):
    if period_start is not None:
        stmt = stmt.where(column >= period_start)

    if period_end is not None:
        stmt = stmt.where(column <= period_end)

    return stmt


def _build_report_title(request: ISPAdminReportCreateRequest) -> str:
    if request.title is not None and request.title.strip():
        return request.title.strip()

    base_title = _REPORT_TITLES.get(request.report_type, "Report")

    if request.period_start is not None and request.period_end is not None:
        return (
            f"{base_title} "
            f"({request.period_start.isoformat()} to {request.period_end.isoformat()})"
        )

    return base_title


async def _count(db: AsyncSession, stmt) -> int:
    result = await db.execute(stmt)
    return int(result.scalar_one() or 0)


async def _group_counts(db: AsyncSession, stmt) -> dict[str, int]:
    result = await db.execute(stmt)
    counts: dict[str, int] = {}

    for key, count in result.all():
        counts[str(key or "unknown")] = int(count or 0)

    return counts


async def _sum_usage_mb(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
) -> Decimal:
    stmt = (
        select(func.coalesce(func.sum(UsageRecord.total_mb), 0))
        .select_from(UsageRecord)
        .join(AppUser, UsageRecord.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
    )

    stmt = _apply_period_filter(
        stmt,
        UsageRecord.record_start,
        period_start,
        period_end,
    )

    result = await db.execute(stmt)
    return Decimal(str(result.scalar_one() or 0))


async def _build_usage_report_data(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
) -> dict:
    analytics_summary = await get_isp_admin_analytics_summary(
        db=db,
        isp_id=isp_id,
        period_start=period_start,
        period_end=period_end,
    )

    return {
        "summary_type": "usage_analytics_summary",
        "summary": analytics_summary.model_dump(mode="json"),
    }


async def _build_alert_report_data(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
) -> dict:
    total_stmt = (
        select(func.count())
        .select_from(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
    )
    total_stmt = _apply_period_filter(total_stmt, Alert.created_at, period_start, period_end)

    unread_stmt = (
        select(func.count())
        .select_from(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(
            AppUser.isp_id == isp_id,
            Alert.status == "unread",
        )
    )
    unread_stmt = _apply_period_filter(unread_stmt, Alert.created_at, period_start, period_end)

    critical_stmt = (
        select(func.count())
        .select_from(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(
            AppUser.isp_id == isp_id,
            Alert.severity == "critical",
        )
    )
    critical_stmt = _apply_period_filter(critical_stmt, Alert.created_at, period_start, period_end)

    type_stmt = (
        select(Alert.alert_type, func.count())
        .select_from(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(Alert.alert_type)
    )
    type_stmt = _apply_period_filter(type_stmt, Alert.created_at, period_start, period_end)

    severity_stmt = (
        select(Alert.severity, func.count())
        .select_from(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(Alert.severity)
    )
    severity_stmt = _apply_period_filter(severity_stmt, Alert.created_at, period_start, period_end)

    return {
        "summary_type": "alert_summary",
        "total_alerts": await _count(db, total_stmt),
        "unread_alerts": await _count(db, unread_stmt),
        "critical_alerts": await _count(db, critical_stmt),
        "counts_by_type": await _group_counts(db, type_stmt),
        "counts_by_severity": await _group_counts(db, severity_stmt),
    }


async def _build_recommendation_report_data(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
) -> dict:
    total_stmt = (
        select(func.count())
        .select_from(Recommendation)
        .join(AppUser, Recommendation.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
    )
    total_stmt = _apply_period_filter(
        total_stmt,
        Recommendation.created_at,
        period_start,
        period_end,
    )

    status_stmt = (
        select(Recommendation.status, func.count())
        .select_from(Recommendation)
        .join(AppUser, Recommendation.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(Recommendation.status)
    )
    status_stmt = _apply_period_filter(
        status_stmt,
        Recommendation.created_at,
        period_start,
        period_end,
    )

    type_stmt = (
        select(Recommendation.recommendation_type, func.count())
        .select_from(Recommendation)
        .join(AppUser, Recommendation.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(Recommendation.recommendation_type)
    )
    type_stmt = _apply_period_filter(
        type_stmt,
        Recommendation.created_at,
        period_start,
        period_end,
    )

    return {
        "summary_type": "recommendation_summary",
        "total_recommendations": await _count(db, total_stmt),
        "counts_by_status": await _group_counts(db, status_stmt),
        "counts_by_type": await _group_counts(db, type_stmt),
    }


async def _build_device_report_data(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
) -> dict:
    total_stmt = (
        select(func.count())
        .select_from(Device)
        .join(AppUser, Device.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
    )
    total_stmt = _apply_period_filter(total_stmt, Device.first_seen, period_start, period_end)

    connected_stmt = (
        select(func.count())
        .select_from(Device)
        .join(AppUser, Device.user_id == AppUser.id)
        .where(
            AppUser.isp_id == isp_id,
            Device.status == "connected",
        )
    )
    connected_stmt = _apply_period_filter(
        connected_stmt,
        Device.first_seen,
        period_start,
        period_end,
    )

    trusted_stmt = (
        select(func.count())
        .select_from(Device)
        .join(AppUser, Device.user_id == AppUser.id)
        .where(
            AppUser.isp_id == isp_id,
            Device.is_trusted.is_(True),
        )
    )
    trusted_stmt = _apply_period_filter(
        trusted_stmt,
        Device.first_seen,
        period_start,
        period_end,
    )

    status_stmt = (
        select(Device.status, func.count())
        .select_from(Device)
        .join(AppUser, Device.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(Device.status)
    )
    status_stmt = _apply_period_filter(status_stmt, Device.first_seen, period_start, period_end)

    type_stmt = (
        select(Device.device_type, func.count())
        .select_from(Device)
        .join(AppUser, Device.user_id == AppUser.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(Device.device_type)
    )
    type_stmt = _apply_period_filter(type_stmt, Device.first_seen, period_start, period_end)

    total_devices = await _count(db, total_stmt)
    trusted_devices = await _count(db, trusted_stmt)

    return {
        "summary_type": "device_summary",
        "total_devices": total_devices,
        "connected_devices": await _count(db, connected_stmt),
        "trusted_devices": trusted_devices,
        "untrusted_devices": total_devices - trusted_devices,
        "counts_by_status": await _group_counts(db, status_stmt),
        "counts_by_type": await _group_counts(db, type_stmt),
    }


async def _build_network_performance_report_data(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
) -> dict:
    total_routers = await _count(
        db,
        select(func.count()).select_from(Router).where(Router.isp_id == isp_id),
    )
    active_routers = await _count(
        db,
        select(func.count()).select_from(Router).where(
            Router.isp_id == isp_id,
            Router.status == "active",
        ),
    )

    total_usage_mb = await _sum_usage_mb(
        db=db,
        isp_id=isp_id,
        period_start=period_start,
        period_end=period_end,
    )
    total_usage_gb = total_usage_mb / Decimal("1024")

    action_status_stmt = (
        select(RouterActionLog.status, func.count())
        .select_from(RouterActionLog)
        .join(Router, RouterActionLog.router_id == Router.id)
        .where(Router.isp_id == isp_id)
        .group_by(RouterActionLog.status)
    )
    action_status_stmt = _apply_period_filter(
        action_status_stmt,
        RouterActionLog.executed_at,
        period_start,
        period_end,
    )

    action_type_stmt = (
        select(RouterActionLog.action_type, func.count())
        .select_from(RouterActionLog)
        .join(Router, RouterActionLog.router_id == Router.id)
        .where(Router.isp_id == isp_id)
        .group_by(RouterActionLog.action_type)
    )
    action_type_stmt = _apply_period_filter(
        action_type_stmt,
        RouterActionLog.executed_at,
        period_start,
        period_end,
    )

    return {
        "summary_type": "network_performance_summary",
        "total_routers": total_routers,
        "active_routers": active_routers,
        "inactive_routers": total_routers - active_routers,
        "total_usage_mb": str(total_usage_mb),
        "total_usage_gb": str(total_usage_gb),
        "router_action_counts_by_status": await _group_counts(db, action_status_stmt),
        "router_action_counts_by_type": await _group_counts(db, action_type_stmt),
    }


async def _build_report_data(
    *,
    db: AsyncSession,
    isp_id: UUID,
    request: ISPAdminReportCreateRequest,
) -> dict:
    period_start = _period_start_to_datetime(request.period_start)
    period_end = _period_end_to_datetime(request.period_end)

    if request.report_type == "usage_report":
        return await _build_usage_report_data(
            db=db,
            isp_id=isp_id,
            period_start=period_start,
            period_end=period_end,
        )

    if request.report_type == "alert_report":
        return await _build_alert_report_data(
            db=db,
            isp_id=isp_id,
            period_start=period_start,
            period_end=period_end,
        )

    if request.report_type == "recommendation_report":
        return await _build_recommendation_report_data(
            db=db,
            isp_id=isp_id,
            period_start=period_start,
            period_end=period_end,
        )

    if request.report_type == "device_report":
        return await _build_device_report_data(
            db=db,
            isp_id=isp_id,
            period_start=period_start,
            period_end=period_end,
        )

    if request.report_type == "network_performance_report":
        return await _build_network_performance_report_data(
            db=db,
            isp_id=isp_id,
            period_start=period_start,
            period_end=period_end,
        )

    raise ValueError(f"Unsupported report type: {request.report_type}")


async def generate_report_for_isp(
    *,
    db: AsyncSession,
    current_admin: Admin,
    request: ISPAdminReportCreateRequest,
) -> Report:
    report_data = await _build_report_data(
        db=db,
        isp_id=current_admin.isp_id,
        request=request,
    )

    report = Report(
        isp_id=current_admin.isp_id,
        generated_by_admin_id=current_admin.id,
        report_type=request.report_type,
        title=_build_report_title(request),
        period_start=request.period_start,
        period_end=request.period_end,
        report_data=report_data,
        file_url=None,
    )

    db.add(report)
    await db.flush()
    await db.refresh(report)

    return report


async def list_reports_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    report_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Report]:
    stmt = (
        select(Report)
        .where(Report.isp_id == isp_id)
        .order_by(Report.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if report_type is not None:
        stmt = stmt.where(Report.report_type == report_type)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_report_for_isp(
    *,
    db: AsyncSession,
    isp_id: UUID,
    report_id: UUID,
) -> Report | None:
    stmt = select(Report).where(
        Report.id == report_id,
        Report.isp_id == isp_id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
