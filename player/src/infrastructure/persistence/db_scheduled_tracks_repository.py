from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, or_, select, update

from application.models.scheduled_tracks import ScheduledTrackModel
from building_blocks.clock import Clock
from domain.breaks import Break
from domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
)
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Identifier
from infrastructure.persistence.database import sessionLocal


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

        with sessionLocal()() as session:
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
            .order_by(ScheduledTrackModel.ordinal)
            .order_by(ScheduledTrackModel.created)
        )
        if break_ is not None:
            stmt = stmt.filter(ScheduledTrackModel.ordinal == break_)
        if played is not None:
            stmt = stmt.filter(ScheduledTrackModel.played == played)

        with sessionLocal()() as session:
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
            start=track.break_.start.astimezone(timezone.utc),
            end=track.break_.end.astimezone(timezone.utc),
            ordinal=track.break_.ordinal,
            duration=track.duration,
            played=False,
            created=now.astimezone(timezone.utc),
            last_changed=now.astimezone(timezone.utc),
        )

        with sessionLocal()() as session:
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
            .where(
                ScheduledTrackModel.start == track.break_.start.astimezone(timezone.utc)
            )
            .where(ScheduledTrackModel.end == track.break_.end.astimezone(timezone.utc))
            .where(ScheduledTrackModel.ordinal == track.break_.ordinal)
            .where(ScheduledTrackModel.played == False)  # noqa: E712
            .where(
                or_(
                    ScheduledTrackModel.duration != track.duration,
                    ScheduledTrackModel.played != track.played,
                )
            )
            .values(duration=track.duration)
            .values(played=track.played)
            .values(last_changed=self._clock.now().astimezone(timezone.utc))
            .execution_options(synchronize_session="fetch")
        )

        with sessionLocal()() as session:
            rowcount = session.execute(stmt).rowcount
            if rowcount > 1:
                raise RuntimeError("More than one track has been updated")
            session.commit()

        to_return = self.get_track_on(
            track.identity, track.break_.date, track.break_.ordinal
        )
        assert to_return is not None
        return to_return

    def insert_or_update(
        self, track: TrackToSchedule | ScheduledTrack
    ) -> ScheduledTrack:
        already_scheduled_track = self.get_track_on(
            track.identity, track.break_.date, track.break_.ordinal
        )
        if already_scheduled_track is None:
            to_scheduled = TrackToSchedule(
                identity=track.identity, break_=track.break_, duration=track.duration
            )
            return self.insert(to_scheduled)

        if isinstance(track, TrackToSchedule):
            scheduled = ScheduledTrack(
                identity=track.identity,
                break_=track.break_,
                duration=track.duration,
                played=already_scheduled_track.played,
                created=already_scheduled_track.created,
                last_changed=self._clock.now(),
            )
            return self.update(scheduled)
        return self.update(track)

    def delete(self, track: ScheduledTrack) -> Optional[ScheduledTrack]:
        stmt = (
            delete(ScheduledTrackModel)
            .where(ScheduledTrackModel.identifier == track.identity.identifier)
            .where(ScheduledTrackModel.provider == track.identity.provider)
            .where(
                ScheduledTrackModel.start == track.break_.start.astimezone(timezone.utc)
            )
            .where(ScheduledTrackModel.end == track.break_.end.astimezone(timezone.utc))
            .where(ScheduledTrackModel.ordinal == track.break_.ordinal)
            .where(ScheduledTrackModel.played == False)  # noqa: E712
            .execution_options(synchronize_session="fetch")
        )
        with sessionLocal()() as session:
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
        with sessionLocal()() as session:
            result = session.execute(stmt).rowcount
            session.commit()
            return result

    def delete_all_with_identity(self, identity: TrackProvidedIdentity) -> int:
        stmt = (
            delete(ScheduledTrackModel)
            .where(ScheduledTrackModel.identifier == identity.identifier)
            .where(ScheduledTrackModel.provider == identity.provider)
            .where(ScheduledTrackModel.played == False)  # noqa: E712
        )

        with sessionLocal()() as session:
            result = session.execute(stmt).rowcount
            session.commit()

        return result

    @staticmethod
    def _set_utc_timezone(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @classmethod
    def _map_on_domain_model(cls, scheduled_track_dict: dict) -> ScheduledTrack:
        identity = TrackProvidedIdentity(
            Identifier(scheduled_track_dict["identifier"]),
            scheduled_track_dict["provider"],
        )
        break_ = Break(
            cls._set_utc_timezone(scheduled_track_dict["start"]),
            cls._set_utc_timezone(scheduled_track_dict["end"]),
            scheduled_track_dict["ordinal"],
        )
        created = cls._set_utc_timezone(scheduled_track_dict["created"])
        last_changed = cls._set_utc_timezone(scheduled_track_dict["last_changed"])
        track_queued = ScheduledTrack(
            identity=identity,
            break_=break_,
            duration=scheduled_track_dict["duration"],
            played=scheduled_track_dict["played"],
            created=created,
            last_changed=last_changed,
        )
        return track_queued
