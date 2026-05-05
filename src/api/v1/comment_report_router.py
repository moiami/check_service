import logging
from uuid import UUID

from fastapi import APIRouter

from src.domain.models.comment_report import (
    CommentReportDeleteDto,
    CommentReportDto,
    CommentReportUpdateDto,
)
from src.services.comment_report_service import (
    comment_report,
    comment_reports,
    delete_comment_report,
    update_comment_report,
)

router = APIRouter(prefix="/api/v1/comment-reports")


@router.get("/")
async def get_comment_reports() -> list[CommentReportDto]:
    logging.info("GET: /api/v1/comment-reports/")
    return await comment_reports()


@router.get("/{id}")
async def get_comment_report(id: UUID) -> CommentReportDto:
    logging.info("GET: /api/v1/comment-reports/%s", id)
    return await comment_report(id)


@router.patch("/")
async def patch_comment_report(data: CommentReportUpdateDto) -> dict[str, str]:
    logging.info("PATCH: /api/v1/comment-reports/")
    return await update_comment_report(data)


@router.delete("/")
async def remove_comment_report(data: CommentReportDeleteDto) -> dict[str, str]:
    logging.info("DELETE: /api/v1/comment-reports/")
    return await delete_comment_report(data)
