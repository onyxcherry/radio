from datetime import date

from kink import inject
from track.domain.breaks import PlayingTime
from track.application.dto import TrackQueued, TrackRequestedAt, TrackEntity
from track.domain.errors import PlayingTimeError
from track.domain.playlist_repository import PlaylistRepository
from track.domain.track import Seconds, TrackUrl


MINIMUM_PLAYING_TIME = Seconds(15)
MAX_TRACKS_QUEUED_ONE_BREAK = 8


@inject
class Playlist:
    # słuchanie eventu REJECTED - trzeba usunąć wszystkie z kolejek z każdego dnia
    def __init__(self, playlist_repository: PlaylistRepository):
        self._playlist_repository = playlist_repository

    def add_at(self, req: TrackRequestedAt, waiting: bool):
        if self.check_played_or_queued_on_day(req.url, req.when.date_, waiting):
            raise PlayingTimeError("Już jest tego dnia")

        left_time = self.get_left_time_on_break(req.when, waiting)
        if left_time <= MINIMUM_PLAYING_TIME:
            raise PlayingTimeError("Not enough time to play")

        tracks_on_break = self.get_tracks_count_on_break(req.when, waiting)
        if tracks_on_break >= MAX_TRACKS_QUEUED_ONE_BREAK:
            raise PlayingTimeError("MAX_QUEUED_EXCEED")

        to_save = TrackQueued(req.url, req.when, waiting)

        self._playlist_repository.save(to_save)
        return ...

    def get_played(self, url: TrackUrl, date_: date) -> list[TrackEntity]: ...

    def get_not_played(self, url: TrackUrl, date_: date) -> list[TrackEntity]: ...

    def get_left_time_on_break(self, when: PlayingTime, waiting) -> int: ...

    def get_tracks_count_on_break(self, when: PlayingTime, waiting) -> int: ...

    def delete_at(self, url: TrackUrl, when: PlayingTime) -> bool: ...

    def check_played_or_queued_on_day(
        self, url: TrackUrl, date_: date, waiting
    ) -> bool: ...

    def check_played_or_queued_at(self, url: TrackUrl, when: PlayingTime) -> bool: ...

    def mark_as_played(self, url: TrackUrl, when: PlayingTime) -> bool:
        pass
