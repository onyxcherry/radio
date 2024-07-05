from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from datetime import datetime
from track.application.models.queue import QueueTrackModel
from track.domain.entities import Status

from .base import Base


class LibraryTrackModel(Base):
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
    duration: Mapped[Optional[int]] = mapped_column(
        Integer, CheckConstraint("duration>0", name="duration_gt_0"), nullable=True
    )
    status: Mapped[Status] = mapped_column(
        Enum(Status, create_contraint=True, native_enum=False),
        # values_callable=lambda x: [e.value for e in x],
        nullable=False,
    )
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    queued_tracks: Mapped[list["QueueTrackModel"]] = relationship()

    def __str__(self) -> str:
        return (
            f"LibraryTrackModel(id={self.id!s}, identifier={self.identifier!s}, "
            f"provider={self.provider!s}, url={self.url!s}, title={self.title!s}, "
            f"duration={self.duration!s}, status={self.status!s}, "
            f"created={self.created!s})"
        )

    def __repr__(self) -> str:
        return (
            f"LibraryTrackModel(id={self.id!r}, identifier={self.identifier!r}, "
            f"provider={self.provider!r}, url={self.url!r}, title={self.title!r}, "
            f"duration={self.duration!r}, status={self.status!s}, "
            f"created={self.created!r})"
        )
