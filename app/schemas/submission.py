from uuid import UUID
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


# ==================== Base ====================

class SubmissionBase(BaseModel):
    team_id: int
    question_id: int
    status: str
    note: str | None = None
    hints_used: int = Field(default=0, ge=0, le=3)
    attempts: int = Field(default=1, ge=1)
    points_awarded: int = Field(default=0, ge=0)


# ==================== Create ====================

class SubmissionCreate(BaseModel):
    question_id: int
    status: Literal["solved", "failed", "skipped"]
    note: str | None = None
    hints_used: int = Field(default=0, ge=0, le=3)
    attempts: int = Field(default=1, ge=1)
    points_awarded: int = Field(default=0, ge=0)


# ==================== Update ====================

class SubmissionUpdate(BaseModel):
    status: str | None = None
    hints_used: int | None = Field(default=None, ge=0, le=3)
    attempts: int | None = Field(default=None, ge=1)
    points_awarded: int | None = Field(default=None, ge=0)


# ==================== Response ====================

class SubmissionResponse(SubmissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)