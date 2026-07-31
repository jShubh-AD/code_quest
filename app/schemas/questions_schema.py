from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import Literal

# ==================== Question Hint ====================

class QuestionHintCreate(BaseModel):
    order_no: int
    text: str
    penalty: int


class QuestionHintResponse(QuestionHintCreate):
    id: UUID
    question_id: int

    model_config = ConfigDict(from_attributes=True)


# ==================== Question Option ====================

class QuestionOptionBase(BaseModel):
    label: Literal["A", "B", "C", "D"]
    text: str

class QuestionOptionCreate(QuestionOptionBase):
    is_correct: bool = False

class QuestionOptionPublic(QuestionOptionBase):
    id: UUID
    question_id: int

    model_config = ConfigDict(from_attributes=True)


class QuestionOptionAdmin(QuestionOptionPublic):
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


# ==================== Question ====================

class QuestionCreate(BaseModel):
    title: str
    description: str
    question_type: Literal["mcq", "qna", "coding", "puzzle"]
    points: int
    time_limit_seconds: int | None = None
    correct_ans: str | None = None
    image_url: str | None = None
    is_active: bool = True

    hints: list[QuestionHintCreate]
    options: list[QuestionOptionCreate]


class QuestionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    question_type: str | None = None
    points: int | None = None
    time_limit_seconds: int | None = None
    correct_ans: str | None = None
    image_url: str | None = None
    is_active: bool | None = None

    hints: list[QuestionHintCreate] | None = None
    options: list[QuestionOptionCreate] | None = None


class QuestionAdminResponse(QuestionCreate):
    id: int
    qr_id: UUID

    hints: list[QuestionHintResponse]
    options: list[QuestionOptionAdmin]

    model_config = ConfigDict(from_attributes=True)

class QuestionPublicResponse(QuestionCreate):
    id: int
    qr_id: UUID

    hints: list[QuestionHintResponse]
    options: list[QuestionOptionPublic]

    model_config = ConfigDict(from_attributes=True)