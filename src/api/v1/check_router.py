import logging

from fastapi import APIRouter

from src.domain.models.check import (
    CheckCommentRequest,
    CheckCommentResponse,
    CheckUserRequest,
    CheckUserResponse,
)
from src.services.check_service import check_comment, check_user

router = APIRouter(prefix="/api/v1/check", tags=["Check"])


@router.post("/comment", summary="Check a comment")
async def post_check_comment(data: CheckCommentRequest) -> CheckCommentResponse:
    logging.info("POST: /api/v1/check/comment")
    return await check_comment(data)


@router.post("/user", summary="Check a user")
async def post_check_user(data: CheckUserRequest) -> CheckUserResponse:
    logging.info("POST: /api/v1/check/user")
    return await check_user(data)
