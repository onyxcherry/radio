import copy
from typing import Optional
from track.application.dto import TrackEntity
from track.domain.library_repository import LibraryRepository
from track.domain.provided import TrackUrl


class InMemoryLibraryRepository(LibraryRepository):
    def __init__(self) -> None:
        self._tracks: dict[TrackUrl, TrackEntity] = {}

    def get(self, track_url: TrackUrl) -> Optional[TrackEntity]:
        if track_url in self._tracks:
            return copy.deepcopy(self._tracks[track_url])
        return None

    def add(self, track: TrackEntity):
        if track.url in self._tracks:
            raise ValueError("Duplicate!")
        self._tracks[track.url] = copy.deepcopy(track)

    def update(self, track: TrackEntity):
        if track.url not in self._tracks:
            raise ValueError("No track already exists!")
        self._tracks[track.url] = copy.deepcopy(track)
