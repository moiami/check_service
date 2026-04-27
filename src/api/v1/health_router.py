import logging

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/health")


@router.get("/")
async def health() -> str:
    logging.info("POST: /api/v1/health/.")
    return 'i\'m alive!'
