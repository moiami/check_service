from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import requests
from fastapi import HTTPException

from src.domain.models.check import CheckCommentRequest, CheckUserRequest
from src.domain.models.llm import LLMPromptResponse
from src.services.check_service import (
    _build_comment_prompt,
    _build_user_prompt,
    _extract_comment_fields,
    _fetch_comment,
    _format_comment_reports,
    _format_reports,
    check_comment,
    check_user,
)


def test_build_comment_prompt_contains_rules_and_comment():
    prompt = _build_comment_prompt("токсичный текст")
    assert "токсичный текст" in prompt
    assert "CONCLUSION=block|everything_is_fine" in prompt
    assert "Ненависть/дискриминация" in prompt


def test_format_comment_reports_empty():
    assert _format_comment_reports([]) == "Отчеты по комментариям: отсутствуют"


def test_format_comment_reports_with_items():
    cr = MagicMock(comment_id=uuid4(), report_text="нарушение")
    text = _format_comment_reports([cr])
    assert str(cr.comment_id) in text
    assert "нарушение" in text


def test_format_reports_empty_and_with_items():
    assert _format_reports([]) == "Предыдущие отчеты по пользователю: отсутствуют"
    report = MagicMock(id=uuid4(), report_text="блокировка")
    text = _format_reports([report])
    assert str(report.id) in text
    assert "блокировка" in text


def test_build_user_prompt_includes_sections():
    cr = MagicMock(comment_id=uuid4(), report_text="плохо")
    report = MagicMock(id=uuid4(), report_text="ранее")
    prompt = _build_user_prompt([cr], [report])
    assert "CONCLUSION=block|everything_is_fine" in prompt
    assert str(cr.comment_id) in prompt
    assert str(report.id) in prompt


def test_extract_comment_fields_success():
    user_id = str(uuid4())
    text, uid = _extract_comment_fields({"text": "hello", "user_id": user_id})
    assert text == "hello"
    assert uid == user_id


@pytest.mark.parametrize(
    "comment",
    [
        {"text": "only text"},
        {"user_id": str(uuid4())},
        {},
    ],
)
def test_extract_comment_fields_missing_fields(comment):
    with pytest.raises(HTTPException) as exc:
        _extract_comment_fields(comment)
    assert exc.value.status_code == 502
    assert exc.value.detail == "Comments service missing fields"


def test_fetch_comment_without_service_url():
    with patch("src.services.check_service.config.COMMENTS_SERVICE_URL", None):
        with pytest.raises(HTTPException) as exc:
            _fetch_comment(str(uuid4()))
    assert exc.value.status_code == 500


def test_fetch_comment_not_found():
    response = MagicMock(status_code=404)
    with (
        patch("src.services.check_service.config.COMMENTS_SERVICE_URL", "http://comments"),
        patch("src.services.check_service.requests.get", return_value=response),
    ):
        with pytest.raises(HTTPException) as exc:
            _fetch_comment(str(uuid4()))
    assert exc.value.status_code == 404
    assert exc.value.detail == "COMMENT NOT FOUND"


def test_fetch_comment_service_unavailable():
    with (
        patch("src.services.check_service.config.COMMENTS_SERVICE_URL", "http://comments"),
        patch(
            "src.services.check_service.requests.get",
            side_effect=requests.RequestException("timeout"),
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            _fetch_comment(str(uuid4()))
    assert exc.value.status_code == 502
    assert exc.value.detail == "Comments service unavailable"


def test_fetch_comment_invalid_json():
    response = MagicMock(status_code=200)
    response.json.side_effect = ValueError("not json")
    with (
        patch("src.services.check_service.config.COMMENTS_SERVICE_URL", "http://comments"),
        patch("src.services.check_service.requests.get", return_value=response),
    ):
        with pytest.raises(HTTPException) as exc:
            _fetch_comment(str(uuid4()))
    assert exc.value.status_code == 502


def test_fetch_comment_success():
    user_id = str(uuid4())
    comment_id = str(uuid4())
    payload = {"text": "ok", "user_id": user_id}
    response = MagicMock(status_code=200)
    response.json.return_value = payload
    with (
        patch("src.services.check_service.config.COMMENTS_SERVICE_URL", "http://comments/"),
        patch("src.services.check_service.requests.get", return_value=response) as get_mock,
    ):
        result = _fetch_comment(comment_id)
    assert result == payload
    get_mock.assert_called_once_with(
        f"http://comments/api/v1/comments/{comment_id}",
        timeout=10,
    )


@pytest.mark.asyncio
async def test_check_comment_creates_report():
    comment_id = uuid4()
    user_id = uuid4()
    report_id = uuid4()
    comment = {"text": "bad", "user_id": str(user_id)}

    with (
        patch(
            "src.services.check_service.asyncio.to_thread",
            new=AsyncMock(return_value=comment),
        ),
        patch(
            "src.services.check_service.prompt_llm",
            new=AsyncMock(return_value=LLMPromptResponse(text="CONCLUSION=block")),
        ),
        patch(
            "src.services.check_service.create_comment_report",
            new=AsyncMock(return_value=report_id),
        ) as create_mock,
    ):
        result = await check_comment(CheckCommentRequest(comment_id=comment_id))

    assert result.comment_report_id == report_id
    create_mock.assert_awaited_once()
    dto = create_mock.await_args.args[0]
    assert dto.comment_id == comment_id
    assert dto.user_id == user_id
    assert dto.report_text == "CONCLUSION=block"


@pytest.mark.asyncio
async def test_check_user_without_violations_skips_llm():
    user_id = uuid4()
    report_id = uuid4()

    with (
        patch(
            "src.services.check_service.get_comment_reports_by_user_id",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "src.services.check_service.get_reports_by_user_id",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "src.services.check_service.prompt_llm",
            new=AsyncMock(),
        ) as llm_mock,
        patch(
            "src.services.check_service.create_report",
            new=AsyncMock(return_value=report_id),
        ) as create_mock,
    ):
        result = await check_user(CheckUserRequest(user_id=user_id))

    assert result.report_id == report_id
    llm_mock.assert_not_awaited()
    dto = create_mock.await_args.args[0]
    assert dto.user_id == user_id
    assert "CONCLUSION=everything_is_fine" in dto.report_text
    assert dto.comment_ids == []
    assert dto.related_report_ids == []


@pytest.mark.asyncio
async def test_check_user_with_history_calls_llm():
    user_id = uuid4()
    report_id = uuid4()
    related_report_id = uuid4()

    cr = MagicMock(comment_id=uuid4(), report_text="токсично")
    prev = MagicMock(id=related_report_id, report_text="старый отчёт")

    with (
        patch(
            "src.services.check_service.get_comment_reports_by_user_id",
            new=AsyncMock(return_value=[cr]),
        ),
        patch(
            "src.services.check_service.get_reports_by_user_id",
            new=AsyncMock(return_value=[prev]),
        ),
        patch(
            "src.services.check_service.prompt_llm",
            new=AsyncMock(return_value=LLMPromptResponse(text="CONCLUSION=block")),
        ) as llm_mock,
        patch(
            "src.services.check_service.create_report",
            new=AsyncMock(return_value=report_id),
        ) as create_mock,
    ):
        result = await check_user(CheckUserRequest(user_id=user_id))

    assert result.report_id == report_id
    llm_mock.assert_awaited_once()
    dto = create_mock.await_args.args[0]
    assert dto.comment_ids == [cr.comment_id]
    assert dto.related_report_ids == [related_report_id]
    assert dto.report_text == "CONCLUSION=block"
