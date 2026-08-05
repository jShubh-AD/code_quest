from uuid import UUID, uuid4
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    SmallInteger,
    String,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.teams import Team
    from app.models.questions_model import Question


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    # solved | failed | skipped

    hints_used: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
    )

    note: Mapped[str] = mapped_column(
        Text,
        nullable= True,
    ) 

    attempts: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
    )

    points_awarded: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    team: Mapped["Team"] = relationship(
        back_populates="submissions"
    )

    question: Mapped["Question"] = relationship(
        back_populates="submissions"
    )

    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "question_id",
            name="uq_team_question_submission",
        ),
        CheckConstraint(
            "hints_used >= 0",
            name="ck_submission_hints_used",
        ),
        CheckConstraint(
            "attempts >= 1",
            name="ck_submission_attempts",
        ),
        CheckConstraint(
            "points_awarded >= 0",
            name="ck_submission_points",
        ),
        CheckConstraint(
            "status IN ('solved', 'failed', 'skipped')",
            name="ck_submission_status",
        ),
    )