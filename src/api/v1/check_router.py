import logging

from fastapi import APIRouter

from src.domain.models.check import CheckCommentRequest, CheckCommentResponse
from src.services.check_service import check_comment

router = APIRouter(prefix="/api/v1/check")


@router.post("/comment")
async def post_check_comment(data: CheckCommentRequest) -> CheckCommentResponse:
    logging.info("POST: /api/v1/check/comment")
    return await check_comment(data)
