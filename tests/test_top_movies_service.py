from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.services.top_movies_service import (
    _already_generated_today,
    _build_movie_prompt,
    _parse_category_review,
)


def test_build_movie_prompt_includes_movie_name_and_views():
    prompt = _build_movie_prompt("Inception", 42)
    assert "Inception" in prompt
    assert "42" in prompt
    assert "Категория:" in prompt


@pytest.mark.parametrize(
    ("text", "expected_category", "expected_review"),
    [
        (
            "Категория: Боевик\nРевью: Отличный фильм.",
            "Боевик",
            "Отличный фильм.",
        ),
        ("просто текст без формата", "Общее", "просто текст без формата"),
    ],
)
def test_parse_category_review(text, expected_category, expected_review):
    category, review = _parse_category_review(text)
    assert category == expected_category
    assert review == expected_review


@pytest.mark.asyncio
async def test_already_generated_today_true_when_latest_is_today():
    today = datetime.now(timezone.utc)
    latest = MagicMock(date=today)

    with patch(
        "src.services.top_movies_service.get_latest_news",
        new=AsyncMock(return_value=latest),
    ):
        assert await _already_generated_today() is True


@pytest.mark.asyncio
async def test_already_generated_today_false_when_no_news():
    with patch(
        "src.services.top_movies_service.get_latest_news",
        new=AsyncMock(return_value=None),
    ):
        assert await _already_generated_today() is False
