from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.data.models.film_review import FilmReview
from src.domain.models.film_review import (
    FilmReviewCreateDto,
    FilmReviewDeleteDto,
    FilmReviewDto,
    FilmReviewUpdateDto,
)
from src.repositories.film_review_repository import (
    delete_film_review as delete,
    get_film_review,
    get_film_reviews,
    insert_film_review as insert,
    update_film_review as update,
)


async def film_reviews() -> list[FilmReviewDto]:
    try:
        return [FilmReviewDto.model_validate(r) for r in await get_film_reviews()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def film_review(id: UUID) -> FilmReviewDto:
    try:
        item = await get_film_review(id)
        if item is None:
            raise TypeError
        return FilmReviewDto.model_validate(item)
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def create_film_review(data: FilmReviewCreateDto) -> dict[str, str]:
    """Internal only — background task triggered by Arseniy's service after AI generates review."""
    try:
        new_review = FilmReview(
            film_id=data.film_id,
            comment_id=data.comment_id,
            new_category=data.new_category,
            review=data.review,
        )
        await insert(new_review)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def update_film_review(data: FilmReviewUpdateDto) -> dict[str, str]:
    try:
        await update(data)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e


async def delete_film_review(data: FilmReviewDeleteDto) -> dict[str, str]:
    try:
        await delete(data.id)
        return {"Info": "Success"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR") from e
