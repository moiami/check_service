from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.data.models.report import Report
from src.domain.models.report import ReportCreateDto, ReportDeleteDto, ReportDto, ReportUpdateDto
from src.repositories.report_repository import (
    delete_report as delete,
    get_report,
    get_reports,
    insert_report as insert,
    update_report as update,
)


def _to_dto(r: Report) -> ReportDto:
    return ReportDto(
        id=r.id,
        user_id=r.user_id,
        date=r.date,
        report_text=r.report_text,
        conclusion=r.conclusion,
        comment_ids=[rc.comment_id for rc in r.comments],
        related_report_ids=[rr.related_report_id for rr in r.related_reports],
    )


async def reports() -> list[ReportDto]:
    try:
        return [_to_dto(r) for r in await get_reports()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def report(id: UUID) -> ReportDto:
    try:
        item = await get_report(id)
        if item is None:
            raise TypeError
        return _to_dto(item)
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def create_report(data: ReportCreateDto) -> UUID:
    """Internal only - called when admin triggers check_comment."""
    try:
        new_report = Report(user_id=data.user_id, report_text=data.report_text)
        return await insert(new_report, data.comment_ids, data.related_report_ids)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def update_report(data: ReportUpdateDto) -> dict[str, str]:
    """Set conclusion (blocking / everything_is_fine) after admin review."""
    try:
        await update(data)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def delete_report(data: ReportDeleteDto) -> dict[str, str]:
    try:
        await delete(data.id)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e
