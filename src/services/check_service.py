import asyncio

import requests
from fastapi import HTTPException
from starlette import status

from src.core import config
from src.domain.models.check import (
    CheckCommentRequest,
    CheckCommentResponse,
    CheckUserRequest,
    CheckUserResponse,
)
from src.domain.models.comment_report import CommentReportCreateDto
from src.domain.models.llm import LLMPromptRequest
from src.domain.models.report import ReportCreateDto
from src.services.comment_report_service import create_comment_report
from src.services.llm_service import prompt_llm
from src.services.report_service import create_report
from src.repositories.comment_report_repository import get_comment_reports_by_user_id
from src.repositories.report_repository import get_reports_by_user_id


async def check_comment(data: CheckCommentRequest) -> CheckCommentResponse:
    comment = await asyncio.to_thread(_fetch_comment, str(data.comment_id))
    comment_text, user_id = _extract_comment_fields(comment)

    prompt = _build_comment_prompt(comment_text)
    llm_response = await prompt_llm(LLMPromptRequest(text=prompt))

    report_id = await create_comment_report(
        CommentReportCreateDto(
            comment_id=data.comment_id,
            user_id=user_id,
            report_text=llm_response.text,
        )
    )

    return CheckCommentResponse(comment_report_id=report_id)


async def check_user(data: CheckUserRequest) -> CheckUserResponse:
    comment_reports = await get_comment_reports_by_user_id(data.user_id)
    reports = await get_reports_by_user_id(data.user_id)

    comment_ids = [cr.comment_id for cr in comment_reports]
    related_report_ids = [r.id for r in reports]

    if not comment_reports and not reports:
        report_text = (
            "Данных о нарушениях нет. "
            "CONCLUSION=everything_is_fine"
        )
    else:
        prompt = _build_user_prompt(comment_reports, reports)
        llm_response = await prompt_llm(LLMPromptRequest(text=prompt))
        report_text = llm_response.text

    report_id = await create_report(
        ReportCreateDto(
            user_id=data.user_id,
            report_text=report_text,
            comment_ids=comment_ids,
            related_report_ids=related_report_ids,
        )
    )

    return CheckUserResponse(report_id=report_id)


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


def _build_comment_prompt(comment_text: str) -> str:
    rules = "\n".join(f"- {rule}" for rule in config.CHECK_COMMENT_RULES)
    return (
        "Ты модератор комментариев. Проверь комментарий по правилам:\n"
        f"{rules}\n\n"
        "Сделай краткий анализ и укажи итог в конце отдельной строкой:\n"
        "CONCLUSION=block|everything_is_fine\n\n"
        "Комментарий:\n"
        f"{comment_text}"
    )


def _build_user_prompt(comment_reports: list, reports: list) -> str:
    rules = "\n".join(f"- {rule}" for rule in config.CHECK_USER_RULES)
    comment_section = _format_comment_reports(comment_reports)
    report_section = _format_reports(reports)

    return (
        "Ты модератор поведения пользователей. Проверь порядочность пользователя по правилам:\n"
        f"{rules}\n\n"
        "Данные для анализа:\n"
        f"{comment_section}\n\n"
        f"{report_section}\n\n"
        "Сделай краткий анализ и укажи итог в конце отдельной строкой:\n"
        "CONCLUSION=block|everything_is_fine"
    )


def _format_comment_reports(comment_reports: list) -> str:
    if not comment_reports:
        return "Отчеты по комментариям: отсутствуют"

    lines = ["Отчеты по комментариям:"]
    for cr in comment_reports:
        lines.append(f"- comment_id={cr.comment_id}: {cr.report_text}")
    return "\n".join(lines)


def _format_reports(reports: list) -> str:
    if not reports:
        return "Предыдущие отчеты по пользователю: отсутствуют"

    lines = ["Предыдущие отчеты по пользователю:"]
    for r in reports:
        lines.append(f"- report_id={r.id}: {r.report_text}")
    return "\n".join(lines)
