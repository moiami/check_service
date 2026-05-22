import os

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/check_db",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import src.repositories.db as db  # noqa: E402

db.engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)
db.async_session = async_sessionmaker(
    bind=db.engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

from src.data.models.comment_report import CommentReport  # noqa: F401,E402
from src.data.models.film_review import FilmReview  # noqa: F401,E402
from src.data.models.news import News, NewsFilmReview  # noqa: F401,E402
from src.data.models.report import Report, ReportComment, ReportRelated  # noqa: F401,E402
from src.domain.models.base import Base  # noqa: E402

engine = db.engine

TABLES = (
    "report_related_reports",
    "report_comments",
    "news_film_reviews",
    "reports",
    "comment_reports",
    "news",
    "film_reviews",
)


async def _db_available() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest_asyncio.fixture(scope="session")
async def db_schema():
    if not await _db_available():
        pytest.skip("PostgreSQL is not available (TEST_DATABASE_URL)")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def clean_db(db_schema):
    async with engine.begin() as conn:
        await conn.execute(
            text(f"TRUNCATE {', '.join(TABLES)} RESTART IDENTITY CASCADE")
        )
