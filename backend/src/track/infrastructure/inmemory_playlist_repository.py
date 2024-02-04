from datetime import date
from track.application.dto import TrackQueued, TrackRequestedAt
from track.domain.playlist_repository import PlaylistRepository
from track.domain.track import TrackUrl


class InMemoryPlaylistRepository(PlaylistRepository):
    def __init__(self) -> None:
        self._tracks: dict[date, list[TrackQueued]] = {}

    def _tracks_at(self, date_: date) -> list[TrackQueued]:
        if date_ not in self._tracks:
            self._tracks[date_] = []
        return self._tracks[date_]

    def get_on(self, track_url: TrackUrl, date_: date) -> list[TrackQueued]:
        on_day = self._tracks_at(date_)
        return list(filter(lambda queued: queued.url == track_url, on_day))

    def filter_on_by(
        self, track_url: TrackUrl, date_: date, conditions
    ) -> list[TrackQueued]:
        ...

    def save(self, track: TrackRequestedAt) -> None:
        queued = TrackQueued(track.url, track.when)
        self._tracks_at(queued.when.date_).append(queued)

    def delete(self, track: TrackQueued) -> None:
        try:
            self._tracks.pop(track.when.date_)
        except KeyError as ex:
            msg = "No queued track can be deleted as no one exists!"
            raise ValueError(msg) from ex
