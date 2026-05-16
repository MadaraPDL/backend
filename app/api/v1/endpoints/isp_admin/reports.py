from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_isp_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.isp_admin import (
    ISPAdminReportCreateRequest,
    ISPAdminReportResponse,
    ISPAdminReportType,
)
from app.services.isp_admin import (
    generate_report_for_isp,
    get_report_for_isp,
    list_reports_for_isp,
)


router = APIRouter(prefix="/reports")


@router.post(
    "",
    response_model=ISPAdminReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report_endpoint(
    request: ISPAdminReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminReportResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    report = await generate_report_for_isp(
        db=db,
        current_admin=current_admin,
        request=request,
    )

    await db.commit()

    return ISPAdminReportResponse.model_validate(report)


@router.get(
    "",
    response_model=list[ISPAdminReportResponse],
)
async def list_reports_endpoint(
    report_type: ISPAdminReportType | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> list[ISPAdminReportResponse]:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    reports = await list_reports_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        report_type=report_type,
        limit=limit,
        offset=offset,
    )

    return [ISPAdminReportResponse.model_validate(report) for report in reports]


@router.get(
    "/{report_id}",
    response_model=ISPAdminReportResponse,
)
async def get_report_endpoint(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_isp_admin),
) -> ISPAdminReportResponse:
    if current_admin.isp_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ISP Admin account is not linked to an ISP",
        )

    report = await get_report_for_isp(
        db=db,
        isp_id=current_admin.isp_id,
        report_id=report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return ISPAdminReportResponse.model_validate(report)
