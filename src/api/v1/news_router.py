import logging
from uuid import UUID

from fastapi import APIRouter

from src.domain.models.news import NewsDeleteDto, NewsDto, NewsUpdateDto
from src.services.news_service import (
    delete_news,
    latest_news_id,
    news,
    news_list,
    update_news,
)

router = APIRouter(prefix="/api/v1/news", tags=["News"])


@router.get("/", summary="List news")
async def get_news_list() -> list[NewsDto]:
    logging.info("GET: /api/v1/news/")
    return await news_list()


@router.get("/latest", summary="Get latest news id")
async def get_latest_news_id() -> dict[str, str]:
    logging.info("GET: /api/v1/news/latest")
    news_id = await latest_news_id()
    return {"news_id": str(news_id)}


@router.get("/{id}", summary="Get news by id")
async def get_news(id: UUID) -> NewsDto:
    logging.info("GET: /api/v1/news/%s", id)
    return await news(id)


@router.patch("/", summary="Update news")
async def patch_news(data: NewsUpdateDto) -> dict[str, str]:
    logging.info("PATCH: /api/v1/news/")
    return await update_news(data)


@router.delete("/", summary="Delete news")
async def remove_news(data: NewsDeleteDto) -> dict[str, str]:
    logging.info("DELETE: /api/v1/news/")
    return await delete_news(data)


