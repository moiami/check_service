from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.domain.models.film_review import (
    FilmReviewCreateDto,
    FilmReviewDeleteDto,
    FilmReviewUpdateDto,
)
from src.services.film_review_service import (
    create_film_review,
    delete_film_review,
    film_review,
    film_reviews,
    update_film_review,
)


@pytest.mark.asyncio
async def test_film_review_crud(clean_db):
    film_id = uuid4()

    review_id = await create_film_review(
        FilmReviewCreateDto(
            film_id=film_id,
            new_category="Драма",
            review="Сильный фильм.",
        )
    )

    item = await film_review(review_id)
    assert item.film_id == film_id
    assert item.new_category == "Драма"
    assert item.review == "Сильный фильм."

    assert await update_film_review(
        FilmReviewUpdateDto(
            id=review_id,
            new_category="Триллер",
            review="Обновлённое ревью.",
        )
    ) == {"Info": "Success"}

    updated = await film_review(review_id)
    assert updated.new_category == "Триллер"
    assert updated.review == "Обновлённое ревью."

    assert await delete_film_review(FilmReviewDeleteDto(id=review_id)) == {
        "Info": "Success"
    }

    with pytest.raises(HTTPException) as exc:
        await film_review(review_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_film_reviews_list(clean_db):
    await create_film_review(
        FilmReviewCreateDto(film_id=uuid4(), new_category="a", review="1")
    )
    await create_film_review(
        FilmReviewCreateDto(film_id=uuid4(), new_category="b", review="2")
    )

    assert len(await film_reviews()) == 2
