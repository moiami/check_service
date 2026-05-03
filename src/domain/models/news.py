from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class NewsDto(BaseModel):
    id: UUID
    date: datetime
    film_review_ids: list[UUID]

    model_config = {"from_attributes": True}


class NewsCreateDto(BaseModel):
    film_review_ids: list[UUID] = []


class NewsUpdateDto(BaseModel):
    id: UUID
    film_review_ids: list[UUID]


class NewsDeleteDto(BaseModel):
    id: UUID
