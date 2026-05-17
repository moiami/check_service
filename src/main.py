import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
import uvicorn

from src.api.v1 import (
    comment_report_router,
    film_review_router,
    health_router,
    news_router,
    report_router,
)
from src.api.v1.check_router import router as check_router
from src.services.top_movies_service import run_daily_top_movies_job

logging.basicConfig(
    level=logging.DEBUG,
    filename="check.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    job = asyncio.create_task(run_daily_top_movies_job())
    try:
        yield
    finally:
        job.cancel()
        with suppress(asyncio.CancelledError):
            await job


app = FastAPI(
    title="Moiami Check Service",
    version="1.0.0",
    description="Service for comment and user checks, plus daily top-movies news generation.",
    openapi_tags=[
        {"name": "Health", "description": "Service health"},
        {"name": "Check", "description": "Checks for comments and users"},
        {"name": "News", "description": "News and latest news id"},
        {"name": "Reports", "description": "User reports"},
        {"name": "Comment reports", "description": "Comment reports"},
        {"name": "Film reviews", "description": "AI film reviews"},
    ],
    lifespan=lifespan,
)
app.include_router(health_router)
app.include_router(report_router)
app.include_router(comment_report_router)
app.include_router(news_router)
app.include_router(film_review_router)
app.include_router(check_router)


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8002)