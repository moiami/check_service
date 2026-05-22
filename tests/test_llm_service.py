import urllib.error
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from src.domain.models.llm import LLMPromptRequest, LLMPromptResponse
from src.services.llm_service import _http_prompt, prompt_llm


@pytest.mark.asyncio
async def test_prompt_llm_echo_when_url_not_set():
    with patch("src.services.llm_service.config.LLM_URL", None):
        result = await prompt_llm(LLMPromptRequest(text="hello"))
    assert result == LLMPromptResponse(text="hello")


@pytest.mark.asyncio
async def test_http_prompt_success():
    with (
        patch("src.services.llm_service.config.LLM_RESPONSE_FIELD", "response"),
        patch("src.services.llm_service.config.LLM_MODEL", "test-model"),
        patch("src.services.llm_service.config.LLM_REQUEST_TEXT_FIELD", "prompt"),
        patch("src.services.llm_service.config.LLM_REQUEST_MODEL_FIELD", "model"),
        patch(
            "src.services.llm_service.asyncio.to_thread",
            new=AsyncMock(return_value={"response": "LLM answer"}),
        ),
    ):
        result = await _http_prompt(
            LLMPromptRequest(text="check this"),
            "http://llm.local/generate",
        )
    assert result.text == "LLM answer"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "side_effect",
    [
        urllib.error.URLError("connection refused"),
        ValueError("invalid json"),
    ],
)
async def test_http_prompt_provider_unavailable(side_effect):
    with patch(
        "src.services.llm_service.asyncio.to_thread",
        new=AsyncMock(side_effect=side_effect),
    ):
        with pytest.raises(HTTPException) as exc:
            await _http_prompt(
                LLMPromptRequest(text="x"),
                "http://llm.local/generate",
            )
    assert exc.value.status_code == 502
    assert exc.value.detail == "LLM provider unavailable"


@pytest.mark.asyncio
async def test_http_prompt_empty_response():
    with (
        patch("src.services.llm_service.config.LLM_RESPONSE_FIELD", "response"),
        patch(
            "src.services.llm_service.asyncio.to_thread",
            new=AsyncMock(return_value={"other": "data"}),
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            await _http_prompt(
                LLMPromptRequest(text="x"),
                "http://llm.local/generate",
            )
    assert exc.value.status_code == 502
    assert exc.value.detail == "LLM provider returned empty response"


@pytest.mark.asyncio
async def test_prompt_llm_delegates_to_http_when_url_set():
    expected = LLMPromptResponse(text="from provider")
    with (
        patch("src.services.llm_service.config.LLM_URL", "http://llm.local"),
        patch(
            "src.services.llm_service._http_prompt",
            new=AsyncMock(return_value=expected),
        ) as http_mock,
    ):
        request = LLMPromptRequest(text="prompt")
        result = await prompt_llm(request)
    assert result == expected
    http_mock.assert_awaited_once_with(request, "http://llm.local")
