import asyncio

import requests
from fastapi import HTTPException
from starlette import status

from src.core import config
from src.domain.models.check import CheckCommentRequest, CheckCommentResponse
from src.domain.models.comment_report import CommentReportCreateDto
from src.domain.models.llm import LLMPromptRequest
from src.services.comment_report_service import create_comment_report
from src.services.llm_service import prompt_llm


async def check_comment(data: CheckCommentRequest) -> CheckCommentResponse:
    comment = await asyncio.to_thread(_fetch_comment, str(data.comment_id))
    comment_text, user_id = _extract_comment_fields(comment)

    prompt = _build_prompt(comment_text)
    llm_response = await prompt_llm(LLMPromptRequest(text=prompt))

    report_id = await create_comment_report(
        CommentReportCreateDto(
            comment_id=data.comment_id,
            user_id=user_id,
            report_text=llm_response.text,
        )
    )

    return CheckCommentResponse(comment_report_id=report_id)


def _fetch_comment(comment_id: str) -> dict:
    base_url = config.COMMENTS_SERVICE_URL
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="COMMENTS_SERVICE_URL is not set",
        )

    url = f"{base_url.rstrip('/')}/api/v1/comments/{comment_id}"
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Comments service unavailable",
        ) from e

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="COMMENT NOT FOUND")

    try:
        return response.json()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Comments service returned invalid response",
        ) from e


def _extract_comment_fields(comment: dict) -> tuple[str, str]:
    comment_text = comment.get("text")
    user_id = comment.get("user_id")
    if not comment_text or not user_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Comments service missing fields",
        )
    return comment_text, user_id


def _build_prompt(comment_text: str) -> str:
    rules = "\n".join(f"- {rule}" for rule in config.CHECK_COMMENT_RULES)
    return (
        "Ты модератор комментариев. Проверь комментарий по правилам:\n"
        f"{rules}\n\n"
        "Сделай краткий анализ и укажи итог в конце отдельной строкой:\n"
        "CONCLUSION=block|everything_is_fine\n\n"
        "Комментарий:\n"
        f"{comment_text}"
    )
