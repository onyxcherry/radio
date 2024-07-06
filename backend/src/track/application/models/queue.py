from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import date, datetime


from .base import Base


class QueueTrackModel(Base):
    __tablename__ = "queue"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    date_: Mapped[date] = mapped_column("date", Date, nullable=False)
    break_: Mapped[int] = mapped_column(
        "break",
        Integer,
        CheckConstraint("break>0", name="break_gt_0"),
        nullable=False,
    )
    played: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    track_id: Mapped[int] = mapped_column(ForeignKey("library.id"))

    def __str__(self) -> str:
        return (
            f"Queue(id={self.id!s}, date={self.date_!s}, "
            f"break={self.break_!s}, played={self.played!s}, "
            f"created={self.created!s}, track_id={self.track_id!s})"
        )

    def __repr__(self) -> str:
        return (
            f"Queue(id={self.id!r}, date_={self.date_!r}, "
            f"break_={self.break_!r}, played={self.played!r}, "
            f"created={self.created!r}, track_id={self.track_id!r})"
        )
