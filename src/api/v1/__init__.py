from src.api.v1.health_router import router as health_router
from src.api.v1.report_router import router as report_router
from src.api.v1.comment_report_router import router as comment_report_router
from src.api.v1.news_router import router as news_router
from src.api.v1.film_review_router import router as film_review_router

__all__ = [
    "health_router",
    "report_router",
    "comment_report_router",
    "news_router",
    "film_review_router",
]