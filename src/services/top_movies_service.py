import asyncio
import logging
import time
from datetime import datetime, timedelta
from uuid import UUID

import requests
from fastapi import HTTPException
from starlette import status

from src.core import config
from src.domain.models.film_review import FilmReviewCreateDto
from src.domain.models.llm import LLMPromptRequest
from src.domain.models.news import NewsCreateDto
from src.repositories.news_repository import get_latest_news
from src.services.film_review_service import create_film_review
from src.services.llm_service import prompt_llm
from src.services.news_service import create_news


async def generate_top_movies_news() -> UUID:
    end = int(time.time())
    start = end - config.TOP_MOVIES_PERIOD_SECONDS
    limit = config.TOP_MOVIES_LIMIT

    movies = await asyncio.to_thread(_fetch_top_movies, start, end, limit)
    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NO MOVIES")

    film_review_ids: list[UUID] = []

    for movie in movies:
        movie_id = UUID(movie.get("id"))
        movie_name = movie.get("name", "")
        views_count = movie.get("views_count", 0)

        prompt = _build_movie_prompt(movie_name, views_count)
        llm_response = await prompt_llm(LLMPromptRequest(text=prompt))
        category, review = _parse_category_review(llm_response.text)

        film_review_id = await create_film_review(
            FilmReviewCreateDto(
                film_id=movie_id,
                new_category=category,
                review=review,
            )
        )
        film_review_ids.append(film_review_id)

    return await create_news(NewsCreateDto(film_review_ids=film_review_ids))


async def run_daily_top_movies_job() -> None:
    async def _run_with_retry() -> None:
        while True:
            try:
                if await _already_generated_today():
                    logging.info("Top movies news already generated today")
                    return
                news_id = await generate_top_movies_news()
                logging.info("Generated top movies news: %s", news_id)
                return
            except Exception:
                logging.exception(
                    "Failed to generate top movies news, retrying in 10 minutes")
                await asyncio.sleep(600)

    await _run_with_retry()

    while True:
        now = datetime.now()
        target = now.replace(
            hour=config.TOP_MOVIES_RUN_HOUR,
            minute=config.TOP_MOVIES_RUN_MINUTE,
            second=0,
            microsecond=0,
        )
        if target <= now:
            target += timedelta(days=1)
        delay = (target - now).total_seconds()
        await asyncio.sleep(delay)
        await _run_with_retry()


def _build_movie_prompt(movie_name: str, views_count: int) -> str:
    return (
        "Ты кинокритик. Для фильма придумай категорию дня и короткое ревью (2-3 предложения).\n"
        "Верни ответ строго в формате:\n"
        "Категория: <категория>\n"
        "Ревью: <текст>\n\n"
        f"Фильм: {movie_name}\n"
        f"Просмотры: {views_count}"
    )


def _parse_category_review(text: str) -> tuple[str, str]:
    category = None
    review = None

    for line in text.splitlines():
        lower = line.lower()
        if lower.startswith("категория:"):
            category = line.split(":", 1)[1].strip()
        if lower.startswith("ревью:"):
            review = line.split(":", 1)[1].strip()

    if not category or not review:
        return "Общее", text

    return category, review


def _fetch_top_movies(start: int, end: int, limit: int) -> list[dict]:
    base_url = config.RESOURCE_SERVICE_URL
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RESOURCE_SERVICE_URL is not set",
        )

    url = f"{base_url.rstrip('/')}/api/v1/catalog/movies/top/"
    params = {
        "start_timestamp": start,
        "end_timestamp": end,
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resource service unavailable",
        ) from e

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resource service error",
        )

    try:
        return response.json()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resource service returned invalid response",
        ) from e


async def _already_generated_today() -> bool:
    latest = await get_latest_news()
    if latest is None:
        return False
    return latest.date.date() == datetime.now().date()
