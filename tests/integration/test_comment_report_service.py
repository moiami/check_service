from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.data.models.comment_report import ConclusionEnum
from src.domain.models.comment_report import (
    CommentReportCreateDto,
    CommentReportDeleteDto,
    CommentReportUpdateDto,
)
from src.services.comment_report_service import (
    comment_report,
    comment_reports,
    create_comment_report,
    delete_comment_report,
    update_comment_report,
)


@pytest.mark.asyncio
async def test_create_and_get_comment_report(clean_db):
    comment_id = uuid4()
    user_id = uuid4()

    report_id = await create_comment_report(
        CommentReportCreateDto(
            comment_id=comment_id,
            user_id=user_id,
            report_text="Токсичный комментарий",
        )
    )

    item = await comment_report(report_id)
    assert item.comment_id == comment_id
    assert item.user_id == user_id
    assert item.report_text == "Токсичный комментарий"
    assert item.conclusion is None


@pytest.mark.asyncio
async def test_comment_reports_list(clean_db):
    await create_comment_report(
        CommentReportCreateDto(
            comment_id=uuid4(),
            user_id=uuid4(),
            report_text="a",
        )
    )
    await create_comment_report(
        CommentReportCreateDto(
            comment_id=uuid4(),
            user_id=uuid4(),
            report_text="b",
        )
    )

    items = await comment_reports()
    assert len(items) == 2


@pytest.mark.asyncio
async def test_update_comment_report(clean_db):
    report_id = await create_comment_report(
        CommentReportCreateDto(
            comment_id=uuid4(),
            user_id=uuid4(),
            report_text="text",
        )
    )

    result = await update_comment_report(
        CommentReportUpdateDto(
            id=report_id,
            conclusion=ConclusionEnum.BLOCKING,
        )
    )
    assert result == {"Info": "Success"}

    item = await comment_report(report_id)
    assert item.conclusion == ConclusionEnum.BLOCKING


@pytest.mark.asyncio
async def test_delete_comment_report(clean_db):
    report_id = await create_comment_report(
        CommentReportCreateDto(
            comment_id=uuid4(),
            user_id=uuid4(),
            report_text="text",
        )
    )

    result = await delete_comment_report(CommentReportDeleteDto(id=report_id))
    assert result == {"Info": "Success"}

    with pytest.raises(HTTPException) as exc:
        await comment_report(report_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_comment_report_not_found(clean_db):
    with pytest.raises(HTTPException) as exc:
        await comment_report(uuid4())
    assert exc.value.status_code == 404
