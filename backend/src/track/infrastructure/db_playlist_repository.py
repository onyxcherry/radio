from datetime import date
from typing import Any, Optional

from sqlalchemy import Select, delete, func, select, update

from track.application.models.library import LibraryTrackModel
from track.application.models.queue import QueueTrackModel
from track.domain.breaks import Breaks, PlayingTime
from track.domain.entities import Status, TrackQueued, TrackToQueue, TrackUnqueued
from track.domain.playlist_repository import PlaylistRepository
from track.domain.provided import Identifier, Seconds, TrackProvidedIdentity
from track.infrastructure.persistence.database import sessionLocal


class DBPlaylistRepository(PlaylistRepository):
    def get_track_on(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> Optional[TrackQueued]:
        stmt = (
            select(
                *QueueTrackModel.__table__.columns,
                LibraryTrackModel.identifier,
                LibraryTrackModel.provider,
                LibraryTrackModel.status,
                LibraryTrackModel.duration,
            )
            .join(LibraryTrackModel)
            .filter(QueueTrackModel.date_ == date_)
            .filter(LibraryTrackModel.identifier == identity.identifier)
            .filter(LibraryTrackModel.provider == identity.provider)
        )
        if break_ is not None:
            stmt = stmt.filter(QueueTrackModel.break_ == break_)

        with sessionLocal()() as session:
            result = session.execute(stmt).one_or_none()
        if result is None:
            return None

        result_dict = result._asdict()

        return self._map_on_domain_model(result_dict)

    def get_all(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> list[TrackQueued]:
        stmt = (
            select(
                *QueueTrackModel.__table__.columns,
                LibraryTrackModel.identifier,
                LibraryTrackModel.provider,
                LibraryTrackModel.status,
                LibraryTrackModel.duration,
            )
            .join(LibraryTrackModel)
            .filter(QueueTrackModel.date_ == date_)
        )
        stmt = self._apply_filters(stmt, break_, played, waiting)

        with sessionLocal()() as session:
            result = session.execute(stmt).all()

        tracks_queued = []
        for row in result:
            row_dict = row._asdict()
            tracks_queued.append(self._map_on_domain_model(row_dict))
        return tracks_queued

    def get_all_by_identity(self, identity: TrackProvidedIdentity) -> list[TrackQueued]:
        track_id = self._get_track_id(identity)
        stmt = (
            select(
                *QueueTrackModel.__table__.columns,
                LibraryTrackModel.identifier,
                LibraryTrackModel.provider,
                LibraryTrackModel.status,
                LibraryTrackModel.duration,
            )
            .join(LibraryTrackModel)
            .filter(QueueTrackModel.track_id == track_id)
        )

        with sessionLocal()() as session:
            result = session.execute(stmt).all()

        tracks_queued = []
        for row in result:
            row_dict = row._asdict()
            tracks_queued.append(self._map_on_domain_model(row_dict))
        return tracks_queued

    def count_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> int:
        stmt = (
            select(func.count(QueueTrackModel.id))
            .join(LibraryTrackModel)
            .filter(QueueTrackModel.date_ == date_)
        )
        stmt = self._apply_filters(stmt, break_, played, waiting)

        with sessionLocal()() as session:
            result = session.execute(stmt).scalar_one()
            return result

    def sum_durations_on(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> Seconds:
        stmt = (
            select(func.sum(LibraryTrackModel.duration))
            .join(QueueTrackModel)
            .filter(QueueTrackModel.date_ == date_)
        )
        stmt = self._apply_filters(stmt, break_, played, waiting)

        with sessionLocal()() as session:
            result = session.execute(stmt).scalar_one()
            if result is None:
                return Seconds(0)
            return Seconds(result)

    def insert(self, track: TrackToQueue) -> TrackQueued:
        track_id = self._get_track_id(track.identity)
        new_queued_track = QueueTrackModel(
            date_=track.when.date_,
            break_=track.when.break_,
            played=track.played,
            track_id=track_id,
        )

        status_stmt = (
            select(LibraryTrackModel.status)
            .filter(LibraryTrackModel.identifier == track.identity.identifier)
            .filter(LibraryTrackModel.provider == track.identity.provider)
        )
        with sessionLocal()() as session:
            session.add(new_queued_track)
            session.commit()
            status = session.execute(status_stmt).one()

        queued = TrackQueued(
            identity=track.identity,
            when=track.when,
            duration=track.duration,
            played=track.played,
            waiting=status[0] == Status.PENDING_APPROVAL,
        )
        return queued

    def update(self, track: TrackQueued) -> TrackQueued:
        track_id = self._get_track_id(track.identity)
        stmt = (
            update(QueueTrackModel)
            .where(QueueTrackModel.date_ == track.when.date_)
            .where(QueueTrackModel.break_ == track.when.break_)
            .where(QueueTrackModel.track_id == track_id)
            .values(played=track.played)
            .execution_options(synchronize_session="fetch")
        )
        with sessionLocal()() as session:
            session.execute(stmt)
            session.commit()

        return track

    def delete(self, track: TrackQueued) -> Optional[TrackUnqueued]:
        track_id = self._get_track_id(track.identity)
        stmt = (
            delete(QueueTrackModel)
            .where(QueueTrackModel.break_ == track.when.break_)
            .where(QueueTrackModel.date_ == track.when.date_)
            .where(QueueTrackModel.track_id == track_id)
            .where(QueueTrackModel.played == False)  # noqa: E712
        )
        with sessionLocal()() as session:
            result = session.execute(stmt).rowcount
            session.commit()
            if result == 0:
                return None
            elif result == 1:
                track_unqueued = TrackUnqueued(identity=track.identity, when=track.when)
                return track_unqueued
            else:
                raise RuntimeError("Why more than 1?!")

    def delete_all(self) -> int:
        stmt = delete(QueueTrackModel)
        with sessionLocal()() as session:
            result = session.execute(stmt).rowcount
            session.commit()
            return result

    def delete_all_with_identity(
        self, identity: TrackProvidedIdentity
    ) -> list[TrackUnqueued]:
        track_id_subquery = (
            select(LibraryTrackModel.id)
            .filter(LibraryTrackModel.identifier == identity.identifier)
            .filter(LibraryTrackModel.provider == identity.provider)
        ).scalar_subquery()
        stmt = select(
            QueueTrackModel.id,
            QueueTrackModel.date_,
            QueueTrackModel.break_,
        ).where(QueueTrackModel.track_id == track_id_subquery)

        tracks_unqueued = []
        ids_to_delete = []

        with sessionLocal()() as session:
            result = session.execute(stmt)

        for data in result:
            data_dict = data._asdict()
            id_ = data_dict["id"]
            break_ = data_dict["break_"]
            date_ = data_dict["date_"]
            pt = PlayingTime(break_=break_, date_=date_)
            track = TrackUnqueued(identity=identity, when=pt)
            tracks_unqueued.append(track)
            ids_to_delete.append(id_)

        stmt = delete(QueueTrackModel).where(QueueTrackModel.id.in_(ids_to_delete))
        with sessionLocal()() as session:
            result = session.execute(stmt).rowcount
            session.commit()

        return tracks_unqueued

    @staticmethod
    def _get_track_id(identity: TrackProvidedIdentity) -> int:
        params: dict[str, Any] = {
            "provider": identity.provider,
            "identifier": identity.identifier,
        }
        stmt = select(LibraryTrackModel.id).filter_by(**params)
        with sessionLocal()() as session:
            result = session.execute(stmt).scalar()
            if result is None:
                raise RuntimeError("No track in library!")
            return result

    @staticmethod
    def _apply_filters(
        stmt: Select,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> Select:
        if break_ is not None:
            stmt = stmt.filter(QueueTrackModel.break_ == break_)
        if played is not None:
            stmt = stmt.filter(QueueTrackModel.played == played)
        if waiting is True:
            stmt = stmt.filter(LibraryTrackModel.status != Status.ACCEPTED)
        elif waiting is False:
            stmt = stmt.filter(LibraryTrackModel.status == Status.ACCEPTED)
        return stmt

    @staticmethod
    def _map_on_domain_model(queue_track_dict: dict) -> TrackQueued:
        identity = TrackProvidedIdentity(
            Identifier(queue_track_dict["identifier"]),
            queue_track_dict["provider"],
        )
        playing_time = PlayingTime(
            date_=queue_track_dict["date"], break_=queue_track_dict["break"]
        )
        track_queued = TrackQueued(
            identity=identity,
            when=playing_time,
            duration=queue_track_dict["duration"],
            played=queue_track_dict["played"],
            waiting=queue_track_dict["status"] != Status.ACCEPTED,
        )
        return track_queued
