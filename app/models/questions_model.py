from uuid import UUID, uuid4

from sqlalchemy import Boolean, SmallInteger, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import  UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.submissison import Submission

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
    )

    qr_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid4,
    )

    qr_code_url: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    # "mcq | coding | puzzle | reasoning | qna" 

    points: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    time_limit_seconds: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    correct_ans: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    hints: Mapped[list["QuestionHint"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionHint.order_no",
    )

    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.label",
    )

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )

# ==================== Hints ====================  

class QuestionHint(Base):
    __tablename__ = "question_hints"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_no: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    penalty: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    question: Mapped["Question"] = relationship(
        back_populates="hints",
    )

# ==================== Options ====================  

class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    question: Mapped["Question"] = relationship(
        back_populates="options",
    )