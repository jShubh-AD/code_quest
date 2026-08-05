from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, functional_validators
from typing import Literal


# ==================== Base ====================

class TeamBase(BaseModel):
    team_name: str
    leader_name: str
    leader_phone: str
    leader_email: str
    semester: int
    course: str

    model_config = ConfigDict(from_attributes=True)


# ==================== Create ====================

class TeamCreate(TeamBase):
    status: Literal["registered", "ongoing", "disqualified", "completed", "winner"] = Field(default="registered")

    pass


# ==================== Update ====================

class TeamUpdate(BaseModel):
    team_tag: str | None = None
    team_name: str | None = None
    leader_name: str | None = None
    leader_phone: str | None = None
    leader_email: str | None = None
    semester: int | None = None
    course: str | None = None
    status: Literal["registered", "ongoing", "disqualified", "completed", "winner"] = Field(default="registered")
    model_config = ConfigDict(from_attributes=True)

# ==================== Response ====================

class TeamResponse(TeamBase):
    id: int
    qr_id: UUID
    status: str
    qr_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VolunteerTeamResponse(TeamBase):
    id: int
    qr_id: UUID
    status: str
    qr_url: str | None = None
    total_points: int = 0
    attempted_questions: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamImport(BaseModel):
    created_at: datetime
    team_name: str
    leader_name: str
    leader_email: str
    leader_phone: str
    course: str
    semester: int

    @field_validator("semester", mode="before")
    @classmethod
    def parse_semester(cls, value):
        # "3rd" -> 3, "5th" -> 5
        digits = "".join(filter(str.isdigit, str(value)))

        if not digits:
            raise ValueError("Invalid semester")

        return int(digits)

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, value):
        if isinstance(value, datetime):
            return value

        return datetime.strptime(
            value,
            "%d/%m/%Y %H:%M:%S",
        )

    model_config = ConfigDict(from_attributes=True)