from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.data.models.report import ConclusionEnum
from src.domain.models.report import ReportCreateDto, ReportDeleteDto, ReportUpdateDto
from src.services.report_service import (
    create_report,
    delete_report,
    report,
    reports,
    update_report,
)


@pytest.mark.asyncio
async def test_create_report_with_links(clean_db):
    user_id = uuid4()
    comment_id = uuid4()
    related_id = uuid4()

    report_id = await create_report(
        ReportCreateDto(
            user_id=user_id,
            report_text="Итоговый отчёт",
            comment_ids=[comment_id],
            related_report_ids=[related_id],
        )
    )

    item = await report(report_id)
    assert item.user_id == user_id
    assert item.report_text == "Итоговый отчёт"
    assert item.comment_ids == [comment_id]
    assert item.related_report_ids == [related_id]


@pytest.mark.asyncio
async def test_update_and_delete_report(clean_db):
    report_id = await create_report(
        ReportCreateDto(user_id=uuid4(), report_text="text")
    )

    assert await update_report(
        ReportUpdateDto(id=report_id, conclusion=ConclusionEnum.EVERYTHING_IS_FINE)
    ) == {"Info": "Success"}

    item = await report(report_id)
    assert item.conclusion == ConclusionEnum.EVERYTHING_IS_FINE

    assert await delete_report(ReportDeleteDto(id=report_id)) == {"Info": "Success"}

    with pytest.raises(HTTPException) as exc:
        await report(report_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_reports_list(clean_db):
    await create_report(ReportCreateDto(user_id=uuid4(), report_text="one"))
    await create_report(ReportCreateDto(user_id=uuid4(), report_text="two"))

    items = await reports()
    assert len(items) == 2
