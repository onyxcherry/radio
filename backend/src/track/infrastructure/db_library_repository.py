from typing import Optional

from sqlalchemy import delete, select, update
from track.application.models.library import LibraryTrackModel
from track.domain.entities import Status, TrackInLibrary
from track.domain.library_repository import LibraryRepository
from track.domain.provided import (
    Identifier,
    ProviderName,
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)
from track.infrastructure.persistence.database import SessionLocal


class DBLibraryRepository(LibraryRepository):
    def get(self, identity: TrackProvidedIdentity) -> Optional[TrackInLibrary]:
        stmt = select(LibraryTrackModel).filter_by(
            provider=identity.provider,
            identifier=identity.identifier,
        )
        with SessionLocal() as session:
            result = session.execute(stmt).one_or_none()
        if result is None:
            return None
        library_track: LibraryTrackModel = result[0]
        return self._map_on_domain_model(library_track)

    def filter_by_statuses(self, statuses: list[Status]) -> list[TrackInLibrary]:
        # paginacja?
        stmt = select(LibraryTrackModel).where(
            LibraryTrackModel.status.in_(statuses),
        )
        with SessionLocal() as session:
            result = session.execute(stmt).all()

        tracks_in_library: list[TrackInLibrary] = []
        for tpl in result:
            if tpl is not None:
                tracks_in_library.append(self._map_on_domain_model(tpl[0]))
        return tracks_in_library

    def add(self, track: TrackInLibrary) -> TrackInLibrary:
        new_track = LibraryTrackModel(
            identifier=track.identity.identifier,
            provider=track.identity.provider,
            title=track.title,
            url=track.url,
            duration=track.duration,
            status=track.status,
        )
        with SessionLocal() as session:
            session.add(new_track)
            session.commit()

        return track

    def update(self, track: TrackInLibrary) -> TrackInLibrary:
        stmt = (
            update(LibraryTrackModel)
            .where(
                (LibraryTrackModel.provider == track.identity.provider)
                & (LibraryTrackModel.identifier == track.identity.identifier)
            )
            .values(
                identifier=track.identity.identifier,
                provider=track.identity.provider,
                title=track.title,
                url=track.url,
                duration=track.duration,
                status=track.status,
            )
            .execution_options(synchronize_session="fetch")
        )
        with SessionLocal() as session:
            session.execute(stmt)
            session.commit()

        return track

    def delete_all(self) -> int:
        with SessionLocal() as session:
            stmt = delete(LibraryTrackModel)
            result = session.execute(stmt)
            session.commit()

            return result.rowcount

    @staticmethod
    def _map_on_domain_model(
        library_track: LibraryTrackModel,
    ) -> TrackInLibrary:
        identity = TrackProvidedIdentity(
            Identifier(library_track.identifier),
            library_track.provider,
        )
        url = TrackUrl(library_track.url) if library_track.url is not None else None
        duration = (
            Seconds(library_track.duration)
            if library_track.duration is not None
            else None
        )
        return TrackInLibrary(
            identity=identity,
            title=library_track.title,
            url=url,
            duration=duration,
            status=library_track.status,
        )
