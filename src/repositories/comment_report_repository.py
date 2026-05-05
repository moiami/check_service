from uuid import UUID

from sqlalchemy import delete, select

from src.data.models.comment_report import CommentReport
from src.domain.models.comment_report import CommentReportUpdateDto
from src.repositories.db import async_session


async def get_comment_reports() -> list[CommentReport]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(CommentReport))
        return list(result.scalars().all())


async def get_comment_reports_by_user_id(user_id: UUID) -> list[CommentReport]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(CommentReport).where(CommentReport.user_id == user_id))
        return list(result.scalars().all())


async def get_comment_report(id: UUID) -> CommentReport:
    async with async_session() as session, session.begin():
        result = await session.execute(select(CommentReport).where(CommentReport.id == id))
        return result.scalar_one_or_none()


async def insert_comment_report(new_cr: CommentReport) -> UUID:
    async with async_session() as session, session.begin():
        session.add(new_cr)
        await session.flush()
        return new_cr.id


async def update_comment_report(cr_in: CommentReportUpdateDto) -> None:
    async with async_session() as session, session.begin():
        cr: CommentReport = (
            await session.execute(select(CommentReport).where(CommentReport.id == cr_in.id))
        ).scalar_one_or_none()
        cr.conclusion = cr_in.conclusion


async def delete_comment_report(id: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(CommentReport).where(CommentReport.id == id))