from typing import Optional
from sqlalchemy import (
    DateTime,
    Enum,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime
from track.application.models.queue import QueuedTrackModel
from track.domain.status import InDatabaseStatus
from sqlalchemy.orm import relationship

from .base import Base


class TrackModel(Base):
    __tablename__ = "library"
    __table_args__ = (UniqueConstraint("identifier", "provider"),)
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[InDatabaseStatus] = mapped_column(
        Enum(InDatabaseStatus, values_callable=lambda x: [e.value for e in x])
    )
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    queuedtracks: Mapped[list[QueuedTrackModel]] = relationship(
        back_populates="librarytrack",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return (
            f"TrackModel(id={self.id!s}, identifier={self.identifier!s}, "
            f"provider={self.provider!s}, url={self.url!s}, title={self.title!s}, "
            f"duration={self.duration!s}, status={self.status!s}, "
            f"created={self.created!s})"
        )

    def __repr__(self) -> str:
        return (
            f"TrackModel(id={self.id!r}, identifier={self.identifier!r}, "
            f"provider={self.provider!r}, url={self.url!r}, title={self.title!r}, "
            f"duration={self.duration!r}, status={self.status!s}, "
            f"created={self.created!r})"
        )
