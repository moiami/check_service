from uuid import UUID

from sqlalchemy import delete, select

from src.data.models.report import Report, ReportComment, ReportRelated
from src.domain.models.report import ReportUpdateDto
from src.repositories.db import async_session


async def get_reports() -> list[Report]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Report))
        return list(result.scalars().all())


async def get_reports_by_user_id(user_id: UUID) -> list[Report]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Report).where(Report.user_id == user_id))
        return list(result.scalars().all())


async def get_report(id: UUID) -> Report:
    async with async_session() as session, session.begin():
        result = await session.execute(select(Report).where(Report.id == id))
        return result.scalar_one_or_none()


async def insert_report(new_report: Report, comment_ids: list[UUID], related_report_ids: list[UUID]) -> UUID:
    async with async_session() as session, session.begin():
        session.add(new_report)
        await session.flush()  # get new_report.id

        for cid in comment_ids:
            session.add(ReportComment(report_id=new_report.id, comment_id=cid))

        for rid in related_report_ids:
            session.add(ReportRelated(report_id=new_report.id, related_report_id=rid))

        return new_report.id


async def update_report(report_in: ReportUpdateDto) -> None:
    async with async_session() as session, session.begin():
        report: Report = (
            await session.execute(select(Report).where(Report.id == report_in.id))
        ).scalar_one_or_none()
        report.conclusion = report_in.conclusion


async def delete_report(id: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(Report).where(Report.id == id))