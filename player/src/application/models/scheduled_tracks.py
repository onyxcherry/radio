from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime

from player.src.domain.types import ProviderName


from .base import Base


class ScheduledTrackModel(Base):
    __tablename__ = "scheduled_tracks"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    provider: Mapped[ProviderName] = mapped_column(String(32), nullable=False)
    start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # TODO: start breaks ordinal from 1
    ordinal: Mapped[int] = mapped_column(
        Integer, CheckConstraint("ordinal>=0", name="ordinal_gte_0"), nullable=False
    )
    duration: Mapped[int] = mapped_column(
        Integer, CheckConstraint("duration>0", name="duration_gt_0"), nullable=False
    )
    played: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    last_changed: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    def __str__(self) -> str:
        return (
            f"ScheduledTrackModel(id={self.id!s}, identifier={self.identifier!s}, "
            f"provider={self.provider!s}, duration={self.duration!s}, start={self.start!s}, "
            f"end={self.end!s}, ordinal={self.ordinal!s}, played={self.played!s}, "
            f"created={self.created!s}, last_changed={self.last_changed!s})"
        )

    def __repr__(self) -> str:
        return (
            f"ScheduledTrackModel(id={self.id!r}, identifier={self.identifier!r}, "
            f"provider={self.provider!r}, duration={self.duration!r}, start={self.start!r}, "
            f"end={self.end!r}, ordinal={self.ordinal!r}, played={self.played!r}, "
            f"created={self.created!r}, last_changed={self.last_changed!r})"
        )
