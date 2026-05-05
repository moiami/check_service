from uuid import UUID

from pydantic import BaseModel


class CheckCommentRequest(BaseModel):
    comment_id: UUID


class CheckCommentResponse(BaseModel):
    comment_report_id: UUID
