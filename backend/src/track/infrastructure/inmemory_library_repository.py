import copy
from typing import Optional
from track.domain.entities import Status, TrackInLibrary
from track.domain.library_repository import LibraryRepository
from track.domain.provided import TrackProvidedIdentity


class InMemoryLibraryRepository(LibraryRepository):
    def __init__(self) -> None:
        self._tracks: dict[TrackProvidedIdentity, TrackInLibrary] = {}

    def _reset_state(self) -> None:
        self._tracks = {}

    def get(self, identity: TrackProvidedIdentity) -> Optional[TrackInLibrary]:
        if identity in self._tracks:
            return copy.deepcopy(self._tracks[identity])
        return None

    def get_all(self):
        return copy.deepcopy(self._tracks)

    def add(self, track: TrackInLibrary) -> TrackInLibrary:
        if track.identity in self._tracks:
            raise ValueError("Duplicate!")
        copied_track = copy.deepcopy(track)
        self._tracks[track.identity] = copied_track
        return copied_track

    def update(self, track: TrackInLibrary) -> TrackInLibrary:
        if track.identity not in self._tracks:
            raise ValueError("No track already exists!")
        copied_track = copy.deepcopy(track)
        self._tracks[track.identity] = copied_track
        return copied_track

    def filter_by_statuses(
        self,
        statuses: list[Status],
    ) -> list[TrackInLibrary]:
        return list(
            filter(
                lambda track: (track.status in statuses),
                self._tracks.values(),
            )
        )
