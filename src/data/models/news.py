from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from src.domain.models.base import Base


class NewsFilmReview(Base):
    """Association: news -> film_review_ids included in this news item."""
    __tablename__ = "news_film_reviews"

    news_id = Column(
        UUID(as_uuid=True),
        ForeignKey("news.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    film_review_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)


class News(Base):
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    film_reviews = relationship(
        "NewsFilmReview",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self) -> None:
        pass  # date is set by server_default; film_reviews appended after insert
