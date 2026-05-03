from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from src.data.models.comment_report import ConclusionEnum


class CommentReportDto(BaseModel):
    id: UUID
    comment_id: UUID
    user_id: UUID
    date: datetime
    report_text: str
    conclusion: ConclusionEnum | None

    model_config = {"from_attributes": True}


class CommentReportCreateDto(BaseModel):
    comment_id: UUID
    user_id: UUID
    report_text: str  # LLM-generated text, passed in by Arseniy's service


class CommentReportUpdateDto(BaseModel):
    id: UUID
    conclusion: ConclusionEnum


class CommentReportDeleteDto(BaseModel):
    id: UUID
