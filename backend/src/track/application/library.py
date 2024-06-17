from typing import Optional
from kink import inject
from track.domain.entities import NewTrack, Status, TrackInLibrary
from track.domain.library_repository import LibraryRepository
from track.domain.provided import TrackProvidedIdentity


@inject
class Library:
    def __init__(self, library_repository: LibraryRepository):
        self._library_repository = library_repository

    def filter_by_statuses(
        self,
        statuses: list[Status],
    ) -> list[TrackInLibrary]:
        return self._library_repository.filter_by_statuses(statuses)

    def get(self, identity: TrackProvidedIdentity) -> Optional[TrackInLibrary]:
        return self._library_repository.get(identity=identity)

    def add(self, track: NewTrack):
        default_status = Status.PENDING_APPROVAL
        track_to_add = TrackInLibrary(
            identity=track.identity,
            title=track.title,
            url=track.url,
            duration=track.duration,
            status=default_status,
        )
        self._library_repository.add(track_to_add)

    def _change_status(
        self, identity: TrackProvidedIdentity, status: Status
    ) -> TrackInLibrary:
        track = self._library_repository.get(identity)
        if track is None:
            raise RuntimeError("No track with given identity")

        track.status = status
        self._library_repository.update(track)
        # emit event
        return track

    def accept(self, identity: TrackProvidedIdentity) -> TrackInLibrary:
        new_status = Status.ACCEPTED
        return self._change_status(identity, new_status)

    def reject(self, identity: TrackProvidedIdentity) -> TrackInLibrary:
        new_status = Status.REJECTED
        return self._change_status(identity, new_status)
