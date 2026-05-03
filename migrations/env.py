import os
import sys
from pathlib import Path
from logging.config import fileConfig

# Add project root to sys.path so `src.*` imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import Base and ALL models so Alembic can see the metadata
from src.domain.models.base import Base
import src.domain.models.report        # noqa: F401  registers Report, ReportComment, ReportRelated
import src.domain.models.comment_report # noqa: F401  registers CommentReport
import src.domain.models.news           # noqa: F401  registers News, NewsFilmReview
import src.domain.models.film_review    # noqa: F401  registers FilmReview

config = context.config

# Allow DATABASE_URL env var to override alembic.ini value (used in Docker)
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
