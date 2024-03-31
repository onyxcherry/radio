from typing import Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date, datetime
from track.domain.status import InDatabaseStatus

from .base import Base


class TrackModel(Base):
    __tablename__ = "library"
    __table_args__ = (UniqueConstraint("identifier", "provider"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[InDatabaseStatus]
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    # queued: Mapped[List["Queue"]] = relationship(
    #     back_populates="track", cascade="all, delete-orphan"
    # )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, title={self.title!r}, url={self.url!r})"


class QueuedTrackModel(Base):
    __tablename__ = "queue"
    __table_args__ = (UniqueConstraint("identifier", "provider"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_: Mapped[date] = mapped_column("date", Date, nullable=False)
    break_: Mapped[int] = mapped_column("break", Integer, nullable=False)
    identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    played: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    track: Mapped["TrackModel"] = relationship(
        TrackModel,
        primaryjoin="TrackModel.id==QueuedTrackModel.id",
        uselist=False,
        foreign_keys=[TrackModel.id],
    )

    def __repr__(self) -> str:
        return f"Queue(id={self.id!r}, date={self.date_!r})"
