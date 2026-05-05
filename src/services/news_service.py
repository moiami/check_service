from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.data.models.news import News
from src.domain.models.news import NewsCreateDto, NewsDeleteDto, NewsDto, NewsUpdateDto
from src.repositories.news_repository import (
    delete_news as delete,
    get_news,
    get_news_list,
    insert_news as insert,
    update_news as update,
)


def _to_dto(n: News) -> NewsDto:
    return NewsDto(
        id=n.id,
        date=n.date,
        film_review_ids=[nfr.film_review_id for nfr in n.film_reviews],
    )


async def news_list() -> list[NewsDto]:
    try:
        return [_to_dto(n) for n in await get_news_list()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def news(id: UUID) -> NewsDto:
    try:
        item = await get_news(id)
        if item is None:
            raise TypeError
        return _to_dto(item)
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def create_news(data: NewsCreateDto) -> dict[str, str]:
    """Internal only - background task"""
    try:
        new_news = News()
        await insert(new_news, data.film_review_ids)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def update_news(data: NewsUpdateDto) -> dict[str, str]:
    try:
        await update(data)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def delete_news(data: NewsDeleteDto) -> dict[str, str]:
    try:
        await delete(data.id)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e
