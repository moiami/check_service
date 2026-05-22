from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.data.models.comment_report import CommentReport
from src.domain.models.comment_report import (
    CommentReportCreateDto,
    CommentReportDeleteDto,
    CommentReportDto,
    CommentReportUpdateDto,
)
from src.repositories.comment_report_repository import (
    delete_comment_report as delete,
    get_comment_report,
    get_comment_reports,
    insert_comment_report as insert,
    update_comment_report as update,
)


async def comment_reports() -> list[CommentReportDto]:
    try:
        return [CommentReportDto.model_validate(r) for r in await get_comment_reports()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def comment_report(id: UUID) -> CommentReportDto:
    try:
        item = await get_comment_report(id)
        if item is None:
            raise TypeError
        return CommentReportDto.model_validate(item)
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def create_comment_report(data: CommentReportCreateDto) -> UUID:
    """
    Internal only - called when LLM generated report_text.
    Flow: admin -> check_comment endpoint -> LLM -> this function saves result.
    """
    try:
        new_cr = CommentReport(
            comment_id=data.comment_id,
            user_id=data.user_id,
            report_text=data.report_text,
            conclusion=data.conclusion,
        )
        return await insert(new_cr)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def update_comment_report(data: CommentReportUpdateDto) -> dict[str, str]:
    """Set conclusion (blocking / everything_is_fine) after admin review."""
    try:
        await update(data)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def delete_comment_report(data: CommentReportDeleteDto) -> dict[str, str]:
    try:
        await delete(data.id)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e
