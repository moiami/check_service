import logging
from uuid import UUID

from fastapi import APIRouter

from src.domain.models.film_review import FilmReviewDeleteDto, FilmReviewDto, FilmReviewUpdateDto
from src.services.film_review_service import (
    delete_film_review,
    film_review,
    film_reviews,
    update_film_review,
)

router = APIRouter(prefix="/api/v1/film-reviews")


@router.get("/")
async def get_film_reviews() -> list[FilmReviewDto]:
    logging.info("GET: /api/v1/film-reviews/")
    return await film_reviews()


@router.get("/{id}")
async def get_film_review(id: UUID) -> FilmReviewDto:
    logging.info("GET: /api/v1/film-reviews/%s", id)
    return await film_review(id)


@router.patch("/")
async def patch_film_review(data: FilmReviewUpdateDto) -> dict[str, str]:
    logging.info("PATCH: /api/v1/film-reviews/")
    return await update_film_review(data)


@router.delete("/")
async def remove_film_review(data: FilmReviewDeleteDto) -> dict[str, str]:
    logging.info("DELETE: /api/v1/film-reviews/")
    return await delete_film_review(data)
