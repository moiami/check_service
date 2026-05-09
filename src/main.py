import logging

from fastapi import FastAPI
import uvicorn

from src.api.v1 import (
    comment_report_router,
    film_review_router,
    health_router,
    news_router,
    report_router,
)

logging.basicConfig(
    level=logging.DEBUG,
    filename="check.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

app = FastAPI()
app.include_router(health_router)
app.include_router(report_router)
app.include_router(comment_report_router)
app.include_router(news_router)
app.include_router(film_review_router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8002)