from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date, datetime


from .base import Base


class QueuedTrackModel(Base):
    __tablename__ = "queue"
    __table_args__ = (UniqueConstraint("identifier", "provider"),)
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    date_: Mapped[date] = mapped_column("date", Date, nullable=False)
    break_: Mapped[int] = mapped_column("break", Integer, nullable=False)
    identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    played: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    created: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    # track: Mapped["TrackModel"] = relationship(
    #     TrackModel,
    #     primaryjoin="TrackModel.id==QueuedTrackModel.id",
    #     uselist=False,
    #     foreign_keys=[TrackModel.id],
    # )
    track_id: Mapped[int] = mapped_column(ForeignKey("library.id"))
    librarytrack: Mapped["TrackModel"] = relationship(
        back_populates="queuedtracks",
        # primaryjoin="TrackModel.id==QueuedTrackModel.id",
    )
    # track: Mapped["TrackModel"] = mapped_column(ForeignKey("library.id"))

    def __str__(self) -> str:
        return f"Queue(id={self.id!s}, date={self.date_!s}, break={self.break_!s}, identifier={self.identifier!s}, provider={self.provider!s}, played={self.played!s}, created={self.created!s}, track_id={self.track_id!s})"

    def __repr__(self) -> str:
        return f"Queue(id={self.id!r}, date_={self.date_!r}, break_={self.break_!r}, identifier={self.identifier!r}, provider={self.provider!r}, played={self.played!r}, created={self.created!r}, track_id={self.track_id!r})"
