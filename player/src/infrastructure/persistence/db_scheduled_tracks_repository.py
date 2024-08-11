from datetime import date
from typing import Any, Optional
from sqlalchemy import func

from sqlalchemy import Select, delete, func, select, update
from player.src.domain.types import Seconds
from player.src.application.models.scheduled_tracks import ScheduledTrackModel
from player.src.building_blocks.clock import Clock
from player.src.domain.breaks import Break
from player.src.domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
)
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository
from player.src.domain.types import Identifier
from player.src.infrastructure.persistence.database import SessionLocal


class DBScheduledTracksRepository(ScheduledTracksRepository):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def get_track_on(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[int] = None,
    ) -> Optional[ScheduledTrack]:
        stmt = (
            select(*ScheduledTrackModel.__table__.columns)
            .filter(ScheduledTrackModel.identifier == identity.identifier)
            .filter(ScheduledTrackModel.provider == identity.provider)
            .filter(func.DATE(ScheduledTrackModel.start) == date_)
            .filter(func.DATE(ScheduledTrackModel.end) == date_)
        )
        if break_ is not None:
            stmt = stmt.filter(ScheduledTrackModel.ordinal == break_)

        with SessionLocal() as session:
            result = session.execute(stmt).one_or_none()
        if result is None:
            return None

        result_dict = result._asdict()

        return self._map_on_domain_model(result_dict)

    def get_all(
        self,
        date_: date,
        break_: Optional[int] = None,
        played: Optional[bool] = None,
    ) -> list[ScheduledTrack]:
        stmt = (
            select(*ScheduledTrackModel.__table__.columns)
            .filter(func.DATE(ScheduledTrackModel.start) == date_)
            .filter(func.DATE(ScheduledTrackModel.end) == date_)
        )
        if break_ is not None:
            stmt = stmt.filter(ScheduledTrackModel.ordinal == break_)
        if played is not None:
            stmt = stmt.filter(ScheduledTrackModel.played == played)

        with SessionLocal() as session:
            result = session.execute(stmt).all()

        tracks_queued = []
        for row in result:
            row_dict = row._asdict()
            tracks_queued.append(self._map_on_domain_model(row_dict))
        return tracks_queued

    def insert(self, track: TrackToSchedule) -> ScheduledTrack:
        already_scheduled = self.get_track_on(
            identity=track.identity,
            date_=track.break_.date,
            break_=track.break_.ordinal,
        )
        if already_scheduled is not None:
            return already_scheduled

        now = self._clock.now()
        scheduled = ScheduledTrackModel(
            identifier=track.identity.identifier,
            provider=track.identity.provider,
            start=track.break_.start,
            end=track.break_.end,
            ordinal=track.break_.ordinal,
            duration=track.duration,
            played=False,
            created=now,
            last_changed=now,
        )

        with SessionLocal() as session:
            session.add(scheduled)
            session.commit()

        return ScheduledTrack(
            identity=track.identity,
            break_=track.break_,
            duration=track.duration,
            played=False,
            created=now,
            last_changed=now,
        )

    def update(self, track: ScheduledTrack) -> ScheduledTrack:
        stmt = (
            update(ScheduledTrackModel)
            .where(ScheduledTrackModel.identifier == track.identity.identifier)
            .where(ScheduledTrackModel.provider == track.identity.provider)
            .where(ScheduledTrackModel.start == track.break_.start)
            .where(ScheduledTrackModel.end == track.break_.end)
            .where(ScheduledTrackModel.ordinal == track.break_.ordinal)
            .where(ScheduledTrackModel.played == False)
            .values(duration=track.duration)
            .values(played=track.played)
            .values(last_changed=self._clock.now())
            .execution_options(synchronize_session="fetch")
        )
        
        with SessionLocal() as session:
            rowcount = session.execute(stmt).rowcount
            if rowcount == 0:
                raise RuntimeError("No object was updated!")
            session.commit()

        return track

    def delete(self, track: ScheduledTrack) -> Optional[ScheduledTrack]:
        stmt = (
            delete(ScheduledTrackModel)
            .where(ScheduledTrackModel.identifier == track.identity.identifier)
            .where(ScheduledTrackModel.provider == track.identity.provider)
            .where(ScheduledTrackModel.start == track.break_.start)
            .where(ScheduledTrackModel.end == track.break_.end)
            .where(ScheduledTrackModel.ordinal == track.break_.ordinal)
            .where(ScheduledTrackModel.played == False)
            .execution_options(synchronize_session="fetch")
        )
        with SessionLocal() as session:
            result = session.execute(stmt).rowcount
            session.commit()

        if result == 0:
            return None
        elif result == 1:
            return track
        else:
            raise RuntimeError("Why more than 1?!")

    def delete_all(self) -> int:
        stmt = delete(ScheduledTrackModel)
        with SessionLocal() as session:
            result = session.execute(stmt).rowcount
            session.commit()
            return result

    def delete_all_with_identity(self, identity: TrackProvidedIdentity) -> int:
        stmt = (
            delete(ScheduledTrackModel)
            .where(ScheduledTrackModel.identifier == identity.identifier)
            .where(ScheduledTrackModel.provider == identity.provider)
            .where(ScheduledTrackModel.played == False)
        )

        with SessionLocal() as session:
            result = session.execute(stmt).rowcount
            session.commit()

        return result

    @staticmethod
    def _map_on_domain_model(scheduled_track_dict: dict) -> ScheduledTrack:
        identity = TrackProvidedIdentity(
            Identifier(scheduled_track_dict["identifier"]),
            scheduled_track_dict["provider"],
        )
        break_ = Break(
            scheduled_track_dict["start"],
            scheduled_track_dict["end"],
            scheduled_track_dict["ordinal"],
        )
        # track_queued = ScheduledTrack(
        #     identity=identity,
        #     break_=break_,
        #     duration=scheduled_track_dict["duration"],
        #     played=scheduled_track_dict["played"],
        #     created=scheduled_track_dict["created"],
        #     last_changed=scheduled_track_dict["last_changed"],
        # )
        track_queued = ScheduledTrack(
            **scheduled_track_dict, identity=identity, break_=break_
        )
        return track_queued