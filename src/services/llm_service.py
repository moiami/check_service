import asyncio
import json
import urllib.error
import urllib.request

from fastapi import HTTPException
from starlette import status

from src.core import config
from src.domain.models.llm import LLMPromptRequest, LLMPromptResponse


async def prompt_llm(data: LLMPromptRequest) -> LLMPromptResponse:
    url = config.LLM_URL
    if not url:
        return LLMPromptResponse(text=data.text)

    return await _http_prompt(data, url)


async def _http_prompt(data: LLMPromptRequest, url: str) -> LLMPromptResponse:
    model = data.model or config.LLM_MODEL
    payload = {
        config.LLM_REQUEST_TEXT_FIELD: data.text,
        "stream": False,
    }
    if model:
        payload[config.LLM_REQUEST_MODEL_FIELD] = model

    def call() -> dict:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    try:
        result = await asyncio.to_thread(call)
    except (urllib.error.URLError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider unavailable",
        ) from e

    response_key = config.LLM_RESPONSE_FIELD
    response_text = result.get(response_key)
    if not response_text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider returned empty response",
        )

    return LLMPromptResponse(text=response_text)
