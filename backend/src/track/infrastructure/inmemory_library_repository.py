import copy
from track.application.dto import TrackEntity
from track.domain.library_repository import LibraryRepository
from track.domain.track import TrackUrl


class InMemoryLibraryRepository(LibraryRepository):
    def __init__(self) -> None:
        self._tracks: dict[TrackUrl, TrackEntity] = {}

    def get(self, track_url: TrackUrl) -> TrackEntity:
        try:
            return copy.deepcopy(self._tracks[track_url])
        except KeyError as error:
            msg = f"Track with url={track_url} was not found!"
            raise ValueError(msg) from error

    def add(self, track: TrackEntity):
        if track.url in self._tracks:
            raise ValueError("Duplicate!")
        self._tracks[track.url] = copy.deepcopy(track)

    def update(self, track: TrackEntity):
        if track.url not in self._tracks:
            raise ValueError("No track already exists!")
        self._tracks[track.url] = copy.deepcopy(track)
