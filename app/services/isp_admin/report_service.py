from __future__ import annotations

from datetime import date, datetime, time, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.report import Report
from app.schemas.isp_admin import ISPAdminReportCreateRequest
from app.services.isp_admin.analytics_service import get_isp_admin_analytics_summary


def _period_start_to_datetime(value: date | None) -> datetime | None:
    if value is None:
        return None

    return datetime.combine(value, time.min, tzinfo=timezone.utc)


def _period_end_to_datetime(value: date | None) -> datetime | None:
    if value is None:
        return None

    return datetime.combine(value, time.max, tzinfo=timezone.utc)


def _build_report_title(request: ISPAdminReportCreateRequest) -> str:
    if request.title is not None and request.title.strip():
        return request.title.strip()

    if request.period_start is not None and request.period_end is not None:
        return (
            f"Usage Report "
            f"({request.period_start.isoformat()} to {request.period_end.isoformat()})"
        )

    return "Usage Report"


async def generate_report_for_isp(
    *,
    db: AsyncSession,
    current_admin: Admin,
    request: ISPAdminReportCreateRequest,
) -> Report:
    period_start_dt = _period_start_to_datetime(request.period_start)
    period_end_dt = _period_end_to_datetime(request.period_end)

    analytics_summary = await get_isp_admin_analytics_summary(
        db=db,
        isp_id=current_admin.isp_id,
        period_start=period_start_dt,
        period_end=period_end_dt,
    )

    report = Report(
        isp_id=current_admin.isp_id,
        generated_by_admin_id=current_admin.id,
        report_type=request.report_type,
        title=_build_report_title(request),
        period_start=request.period_start,
        period_end=request.period_end,
        report_data={
            "summary_type": "usage_analytics_summary",
            "summary": analytics_summary.model_dump(mode="json"),
        },
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
