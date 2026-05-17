from uuid import uuid4

from sqlalchemy import UUID, Column, Text

from src.domain.models.base import Base


class FilmReview(Base):
    __tablename__ = "film_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    film_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    new_category = Column(Text, nullable=False)
    review = Column(Text, nullable=False)

    def __init__(
        self,
        film_id,
        new_category: str,
        review: str,
    ) -> None:
        self.film_id = film_id
        self.new_category = new_category
        self.review = review
