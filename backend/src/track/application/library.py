from typing import Optional
from kink import inject
from track.application.dto import NewTrack, TrackEntity
from track.domain.errors import TrackDurationExceeded
from track.domain.library_repository import LibraryRepository
from track.domain.status import Status
from track.domain.track import Seconds, TrackUrl

MAX_TRACK_DURATION_SECONDS = Seconds(1200)


@inject
class Library:
    def __init__(self, library_repository: LibraryRepository):
        self._library_repository = library_repository

    def _check_valid_duration(self, track_duration: Seconds, limit: Seconds) -> bool:
        return track_duration <= limit

    def filter_by_status(self, status: Status) -> list[TrackEntity]:
        ...

    def get(self, track_url: TrackUrl) -> Optional[TrackEntity]:
        self._library_repository.get(track_url)

    def add(self, track: NewTrack):
        length_limit = MAX_TRACK_DURATION_SECONDS
        if not self._check_valid_duration(track.duration, length_limit):
            msg = f"Too long track. Limit is {length_limit}"
            raise TrackDurationExceeded(msg)

        track_to_add = TrackEntity(
            title=track.title,
            url=track.url,
            duration=track.duration,
            status=Status.PENDING_APPROVAL,
            ready=False,
            # wywalić to, mieszanie odpowiedzialności playera to jest
        )
        self._library_repository.add(track_to_add)

    def accept(self, track_url: TrackUrl) -> None:
        track = self._library_repository.get(track_url)
        track.status = Status.ACCEPTED
        self._library_repository.update(track)

    def reject(self, track_url: TrackUrl) -> None:
        track = self._library_repository.get(track_url)
        track.status = Status.REJECTED
        self._library_repository.update(track)
