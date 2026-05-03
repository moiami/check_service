from uuid import UUID

from pydantic import BaseModel


class FilmReviewDto(BaseModel):
    id: UUID
    film_id: UUID
    comment_id: UUID
    new_category: str
    review: str

    model_config = {"from_attributes": True}


class FilmReviewCreateDto(BaseModel):
    film_id: UUID
    comment_id: UUID
    new_category: str
    review: str


class FilmReviewUpdateDto(BaseModel):
    id: UUID
    new_category: str
    review: str


class FilmReviewDeleteDto(BaseModel):
    id: UUID
