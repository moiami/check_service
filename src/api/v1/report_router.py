import logging
from uuid import UUID

from fastapi import APIRouter

from src.domain.models.report import ReportDeleteDto, ReportDto, ReportUpdateDto
from src.services.report_service import (
    delete_report,
    report,
    reports,
    update_report,
)

router = APIRouter(prefix="/api/v1/reports")


@router.get("/")
async def get_reports() -> list[ReportDto]:
    logging.info("GET: /api/v1/reports/")
    return await reports()


@router.get("/{id}")
async def get_report(id: UUID) -> ReportDto:
    logging.info("GET: /api/v1/reports/%s", id)
    return await report(id)


@router.patch("/")
async def patch_report(data: ReportUpdateDto) -> dict[str, str]:
    logging.info("PATCH: /api/v1/reports/")
    return await update_report(data)


@router.delete("/")
async def remove_report(data: ReportDeleteDto) -> dict[str, str]:
    logging.info("DELETE: /api/v1/reports/")
    return await delete_report(data)
