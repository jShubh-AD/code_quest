from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


# ==================== Base ====================

class TeamBase(BaseModel):
    team_tag: str
    team_name: str
    leader_name: str
    leader_phone: str
    leader_email: str
    semester: int
    course: str

    model_config = ConfigDict(from_attributes=True)


# ==================== Create ====================

class TeamCreate(TeamBase):
    status: Literal["pending","registered","rejected", "winner"] = Field(default="registered")
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
    status: Literal["pending","registered","rejected", "winner"] = Field(default="registered")

    model_config = ConfigDict(from_attributes=True)


# ==================== Response ====================

class TeamResponse(TeamBase):
    id: UUID
    qr_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)