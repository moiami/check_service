from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from src.data.models.report import ConclusionEnum


class ReportDto(BaseModel):
    id: UUID
    user_id: UUID
    date: datetime
    report_text: str
    conclusion: ConclusionEnum | None
    comment_ids: list[UUID]
    related_report_ids: list[UUID]

    model_config = {"from_attributes": True}


class ReportCreateDto(BaseModel):
    user_id: UUID
    report_text: str
    comment_ids: list[UUID] = []
    related_report_ids: list[UUID] = []


class ReportUpdateDto(BaseModel):
    id: UUID
    conclusion: ConclusionEnum


class ReportDeleteDto(BaseModel):
    id: UUID
