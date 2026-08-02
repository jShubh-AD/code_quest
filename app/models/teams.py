from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import  String, DateTime, func, SmallInteger, Text
from app.core.db import Base
from uuid import uuid4, UUID
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.members import Member

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True
    )

    team_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    leader_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    leader_phone: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False
    )

    leader_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    semester: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    course: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    ) 

    qr_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        index=True,
        default=uuid4,
    )

    qr_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="registered"
    )

    created_at: Mapped[datetime] =mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        onupdate=func.now(),
        server_default=func.now()
    )

    members: Mapped[list["Member"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan"
    )