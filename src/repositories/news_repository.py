from uuid import UUID

from sqlalchemy import delete, select

from src.data.models.news import News, NewsFilmReview
from src.domain.models.news import NewsUpdateDto
from src.repositories.db import async_session


async def get_news_list() -> list[News]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(News))
        return list(result.scalars().all())


async def get_news(id: UUID) -> News:
    async with async_session() as session, session.begin():
        result = await session.execute(select(News).where(News.id == id))
        return result.scalar_one()


async def insert_news(new_news: News, film_review_ids: list[UUID]) -> None:
    async with async_session() as session, session.begin():
        session.add(new_news)
        await session.flush()

        for frid in film_review_ids:
            session.add(NewsFilmReview(news_id=new_news.id, film_review_id=frid))


async def update_news(news_in: NewsUpdateDto) -> None:
    async with async_session() as session, session.begin():
        # replace film_review links entirely
        await session.execute(
            delete(NewsFilmReview).where(NewsFilmReview.news_id == news_in.id)
        )
        for frid in news_in.film_review_ids:
            session.add(NewsFilmReview(news_id=news_in.id, film_review_id=frid))


async def delete_news(id: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(News).where(News.id == id))
