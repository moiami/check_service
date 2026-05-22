import enum
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from src.domain.models.base import Base


class ConclusionEnum(str, enum.Enum):
    BLOCKING = "blocking"
    EVERYTHING_IS_FINE = "everything_is_fine"


class ReportComment(Base):
    """Association: report -> comment_ids that triggered this report."""
    __tablename__ = "report_comments"

    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    comment_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)


class ReportRelated(Base):
    """Association: report -> previous report_ids linked to this report."""
    __tablename__ = "report_related_reports"

    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    related_report_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    report_text = Column(Text, nullable=False)
    conclusion = Column(Text, nullable=True)  # set after admin review

    comments = relationship(
        "ReportComment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    related_reports = relationship(
        "ReportRelated",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(
        self,
        user_id,
        report_text: str,
        conclusion: ConclusionEnum | str | None = None,
    ) -> None:
        self.user_id = user_id
        self.report_text = report_text
        if isinstance(conclusion, ConclusionEnum):
            self.conclusion = conclusion.value
        else:
            self.conclusion = conclusion
