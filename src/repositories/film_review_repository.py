from uuid import UUID

from sqlalchemy import delete, select

from src.data.models.film_review import FilmReview
from src.domain.models.film_review import FilmReviewUpdateDto
from src.repositories.db import async_session


async def get_film_reviews() -> list[FilmReview]:
    async with async_session() as session, session.begin():
        result = await session.execute(select(FilmReview))
        return list(result.scalars().all())


async def get_film_review(id: UUID) -> FilmReview:
    async with async_session() as session, session.begin():
        result = await session.execute(select(FilmReview).where(FilmReview.id == id))
        return result.scalar_one_or_none()


async def insert_film_review(new_review: FilmReview) -> UUID:
    async with async_session() as session, session.begin():
        session.add(new_review)
        await session.flush()
        return new_review.id


async def update_film_review(review_in: FilmReviewUpdateDto) -> None:
    async with async_session() as session, session.begin():
        review: FilmReview = (
            await session.execute(select(FilmReview).where(FilmReview.id == review_in.id))
        ).scalar_one_or_none()
        review.new_category = review_in.new_category
        review.review = review_in.review


async def delete_film_review(id: UUID) -> None:
    async with async_session() as session, session.begin():
        await session.execute(delete(FilmReview).where(FilmReview.id == id))