from datetime import date
from typing import Optional

from kink import inject
from track.domain.entities import TrackQueued, TrackRequested, TrackToQueue
from track.domain.breaks import Breaks, PlayingTime
from track.domain.playlist_repository import PlaylistRepository
from track.domain.provided import Seconds, TrackProvidedIdentity


@inject
class Playlist:
    # słuchanie eventu REJECTED - trzeba usunąć wszystkie z kolejek z każdego dnia
    def __init__(self, playlist_repository: PlaylistRepository):
        self._playlist_repository = playlist_repository

    def get(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[Breaks] = None,
    ):
        return self._playlist_repository.get_track_on(identity, date_, break_)

    def get_all(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ):
        return self._playlist_repository.get_all(
            date_,
            break_,
            played,
            waiting,
        )

    def add(self, req: TrackRequested) -> TrackQueued:
        to_save = TrackToQueue(
            req.identity,
            req.when,
            played=False,
        )
        saved = self._playlist_repository.insert(to_save)
        return saved

    def delete(self, track: TrackQueued) -> Optional[TrackQueued]:
        return self._playlist_repository.delete(track)

    def mark_as_played(self, track: TrackQueued) -> TrackQueued:
        to_save = track
        assert track.waiting is False
        to_save.played = True
        saved = self._playlist_repository.update(to_save)
        return saved

    def get_tracks_duration_on_break(
        self,
        when: PlayingTime,
        waiting: Optional[bool] = None,
    ) -> Seconds:
        return self._playlist_repository.sum_durations_on(
            when.date_, when.break_, played=False, waiting=waiting
        )

    def get_tracks_count_on_break(
        self,
        when: PlayingTime,
        waiting: Optional[bool] = None,
    ) -> int:
        return self._playlist_repository.count_on(
            when.date_, when.break_, played=False, waiting=waiting
        )

    def check_played_or_queued_on_day(
        self, identity: TrackProvidedIdentity, date_: date
    ) -> bool:
        got_track = self._playlist_repository.get_track_on(identity, date_)
        return got_track is not None and got_track.waiting is False
