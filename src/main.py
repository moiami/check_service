import logging

from fastapi import FastAPI

from src.api.v1 import health_router

logging.basicConfig(
    level=logging.DEBUG,
    filename="check.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

app = FastAPI()
app.include_router(health_router)
