from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.teams import Team


class Member(Base):
    __tablename__ = "members"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    team_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_no: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    is_leader: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    course: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    semester: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    team: Mapped["Team"] = relationship(
        back_populates="members",
    )