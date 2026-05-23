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
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
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


def _iso(value) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _to_number_string(value) -> str:
    if value is None:
        return "0"

    return str(value)


def _insight(message: str, severity: str = "info") -> dict:
    return {
        "severity": severity,
        "message": message,
    }


async def _recent_alert_rows(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
    limit: int = 10,
) -> list[dict]:
    stmt = (
        select(
            Alert.id,
            Alert.alert_type,
            Alert.severity,
            Alert.title,
            Alert.message,
            Alert.status,
            Alert.created_at,
            AppUser.full_name,
            AppUser.email,
            UserSubscription.subscription_label,
        )
        .select_from(Alert)
        .join(AppUser, Alert.user_id == AppUser.id)
        .join(UserSubscription, Alert.user_subscription_id == UserSubscription.id)
        .where(AppUser.isp_id == isp_id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    stmt = _apply_period_filter(stmt, Alert.created_at, period_start, period_end)

    result = await db.execute(stmt)

    return [
        {
            "alert_id": str(alert_id),
            "user": full_name,
            "email": email,
            "service_line": subscription_label,
            "type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "status": status,
            "created_at": _iso(created_at),
        }
        for (
            alert_id,
            alert_type,
            severity,
            title,
            message,
            status,
            created_at,
            full_name,
            email,
            subscription_label,
        ) in result.all()
    ]


async def _top_service_line_usage_rows(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
    limit: int = 10,
) -> list[dict]:
    stmt = (
        select(
            AppUser.full_name,
            AppUser.email,
            UserSubscription.subscription_label,
            SubscriptionPlan.plan_name,
            func.coalesce(func.sum(UsageRecord.total_mb), 0).label("total_mb"),
        )
        .select_from(UsageRecord)
        .join(AppUser, UsageRecord.user_id == AppUser.id)
        .join(UserSubscription, UsageRecord.user_subscription_id == UserSubscription.id)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .where(AppUser.isp_id == isp_id)
        .group_by(
            AppUser.full_name,
            AppUser.email,
            UserSubscription.subscription_label,
            SubscriptionPlan.plan_name,
        )
        .order_by(func.coalesce(func.sum(UsageRecord.total_mb), 0).desc())
        .limit(limit)
    )
    stmt = _apply_period_filter(stmt, UsageRecord.record_start, period_start, period_end)

    result = await db.execute(stmt)

    rows = []
    for full_name, email, service_line, plan_name, total_mb in result.all():
        total_mb_decimal = Decimal(str(total_mb or 0))
        rows.append(
            {
                "user": full_name,
                "email": email,
                "service_line": service_line,
                "package": plan_name,
                "total_mb": _to_number_string(total_mb_decimal),
                "total_gb": _to_number_string(total_mb_decimal / Decimal("1024")),
            }
        )

    return rows


async def _top_router_usage_rows(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
    limit: int = 10,
) -> list[dict]:
    stmt = (
        select(
            Router.router_name,
            Router.router_model,
            Router.router_ip,
            AppUser.full_name,
            UserSubscription.subscription_label,
            SubscriptionPlan.plan_name,
            func.coalesce(func.sum(UsageRecord.total_mb), 0).label("total_mb"),
        )
        .select_from(UsageRecord)
        .join(Router, UsageRecord.router_id == Router.id)
        .join(AppUser, UsageRecord.user_id == AppUser.id)
        .join(UserSubscription, UsageRecord.user_subscription_id == UserSubscription.id)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .where(Router.isp_id == isp_id)
        .group_by(
            Router.router_name,
            Router.router_model,
            Router.router_ip,
            AppUser.full_name,
            UserSubscription.subscription_label,
            SubscriptionPlan.plan_name,
        )
        .order_by(func.coalesce(func.sum(UsageRecord.total_mb), 0).desc())
        .limit(limit)
    )
    stmt = _apply_period_filter(stmt, UsageRecord.record_start, period_start, period_end)

    result = await db.execute(stmt)

    rows = []
    for router_name, router_model, router_ip, user_name, service_line, plan_name, total_mb in result.all():
        total_mb_decimal = Decimal(str(total_mb or 0))
        rows.append(
            {
                "router": router_name,
                "model": router_model,
                "ip": str(router_ip) if router_ip is not None else None,
                "user": user_name,
                "service_line": service_line,
                "package": plan_name,
                "total_mb": _to_number_string(total_mb_decimal),
                "total_gb": _to_number_string(total_mb_decimal / Decimal("1024")),
            }
        )

    return rows


async def _recent_usage_rows(
    *,
    db: AsyncSession,
    isp_id: UUID,
    period_start: datetime | None,
    period_end: datetime | None,
    limit: int = 10,
) -> list[dict]:
    stmt = (
        select(
            UsageRecord.id,
            UsageRecord.upload_mb,
            UsageRecord.download_mb,
            UsageRecord.total_mb,
            UsageRecord.record_start,
            UsageRecord.record_end,
            UsageRecord.source,
            Router.router_name,
            AppUser.full_name,
            UserSubscription.subscription_label,
            SubscriptionPlan.plan_name,
        )
        .select_from(UsageRecord)
        .join(Router, UsageRecord.router_id == Router.id)
        .join(AppUser, UsageRecord.user_id == AppUser.id)
        .join(UserSubscription, UsageRecord.user_subscription_id == UserSubscription.id)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .where(Router.isp_id == isp_id)
        .order_by(UsageRecord.record_start.desc())
        .limit(limit)
    )
    stmt = _apply_period_filter(stmt, UsageRecord.record_start, period_start, period_end)

    result = await db.execute(stmt)

    return [
        {
            "usage_id": str(usage_id),
            "user": user_name,
            "router": router_name,
            "service_line": service_line,
            "package": plan_name,
            "upload_mb": _to_number_string(upload_mb),
            "download_mb": _to_number_string(download_mb),
            "total_mb": _to_number_string(total_mb),
            "source": source,
            "record_start": _iso(record_start),
            "record_end": _iso(record_end),
        }
        for (
            usage_id,
            upload_mb,
            download_mb,
            total_mb,
            record_start,
            record_end,
            source,
            router_name,
            user_name,
            service_line,
            plan_name,
        ) in result.all()
    ]


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

    summary = analytics_summary.model_dump(mode="json")
    total_usage_gb = Decimal(str(summary.get("total_usage_gb") or 0))

    insights = []

    if total_usage_gb > 0:
        insights.append(
            _insight(
                f"Total usage for this period is {total_usage_gb:.2f} GB.",
                "info",
            )
        )
    else:
        insights.append(
            _insight(
                "No usage was recorded for this report period.",
                "warning",
            )
        )

    pending_requests = int(summary.get("pending_plan_change_requests") or 0)

    if pending_requests:
        insights.append(
            _insight(
                f"{pending_requests} pending service/package request(s) may need review.",
                "warning",
            )
        )

    return {
        "summary_type": "usage_analytics_summary",
        "summary": summary,
        "insights": insights,
        "tables": {
            "top_service_lines_by_usage": await _top_service_line_usage_rows(
                db=db,
                isp_id=isp_id,
                period_start=period_start,
                period_end=period_end,
            ),
            "top_routers_by_usage": await _top_router_usage_rows(
                db=db,
                isp_id=isp_id,
                period_start=period_start,
                period_end=period_end,
            ),
            "recent_usage_records": await _recent_usage_rows(
                db=db,
                isp_id=isp_id,
                period_start=period_start,
                period_end=period_end,
            ),
        },
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

    total_alerts = await _count(db, total_stmt)
    unread_alerts = await _count(db, unread_stmt)
    critical_alerts = await _count(db, critical_stmt)
    counts_by_type = await _group_counts(db, type_stmt)
    counts_by_severity = await _group_counts(db, severity_stmt)

    insights = []

    if unread_alerts:
        insights.append(
            _insight(
                f"{unread_alerts} unread alert(s) still need review.",
                "warning",
            )
        )

    if critical_alerts:
        insights.append(
            _insight(
                f"{critical_alerts} critical alert(s) require immediate attention.",
                "critical",
            )
        )

    if not insights:
        insights.append(
            _insight(
                "No critical alert pressure detected in this report period.",
                "success",
            )
        )

    return {
        "summary_type": "alert_summary",
        "total_alerts": total_alerts,
        "unread_alerts": unread_alerts,
        "critical_alerts": critical_alerts,
        "counts_by_type": counts_by_type,
        "counts_by_severity": counts_by_severity,
        "insights": insights,
        "tables": {
            "recent_alerts": await _recent_alert_rows(
                db=db,
                isp_id=isp_id,
                period_start=period_start,
                period_end=period_end,
            ),
        },
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
