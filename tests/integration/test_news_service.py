from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.domain.models.news import NewsCreateDto, NewsDeleteDto, NewsUpdateDto
from src.services.film_review_service import create_film_review
from src.services.news_service import (
    create_news,
    delete_news,
    latest_news_id,
    news,
    news_list,
    update_news,
)
from src.domain.models.film_review import FilmReviewCreateDto


@pytest.mark.asyncio
async def test_news_with_film_reviews(clean_db):
    fr_id = await create_film_review(
        FilmReviewCreateDto(
            film_id=uuid4(),
            new_category="Комедия",
            review="Смешно.",
        )
    )

    news_id = await create_news(NewsCreateDto(film_review_ids=[fr_id]))

    item = await news(news_id)
    assert item.film_review_ids == [fr_id]

    new_fr_id = await create_film_review(
        FilmReviewCreateDto(
            film_id=uuid4(),
            new_category="Ужасы",
            review="Страшно.",
        )
    )
    assert await update_news(
        NewsUpdateDto(id=news_id, film_review_ids=[new_fr_id])
    ) == {"Info": "Success"}

    updated = await news(news_id)
    assert updated.film_review_ids == [new_fr_id]


@pytest.mark.asyncio
async def test_latest_news_id(clean_db):
    first = await create_news(NewsCreateDto())
    second = await create_news(NewsCreateDto())

    assert await latest_news_id() == second
    assert second != first


@pytest.mark.asyncio
async def test_latest_news_id_not_found(clean_db):
    with pytest.raises(HTTPException) as exc:
        await latest_news_id()
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_news(clean_db):
    news_id = await create_news(NewsCreateDto())
    assert await delete_news(NewsDeleteDto(id=news_id)) == {"Info": "Success"}

    with pytest.raises(HTTPException) as exc:
        await news(news_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_news_list(clean_db):
    await create_news(NewsCreateDto())
    await create_news(NewsCreateDto())

    assert len(await news_list()) == 2
