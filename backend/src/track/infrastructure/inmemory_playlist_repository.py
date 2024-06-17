from datetime import date
from typing import Optional

from track.domain.breaks import Breaks
from track.domain.entities import TrackQueued
from track.domain.provided import Seconds, TrackProvidedIdentity
from track.domain.playlist_repository import PlaylistRepository


class InMemoryPlaylistRepository(PlaylistRepository):
    def __init__(self) -> None:
        self._tracks: dict[date, dict[Breaks, list[TrackQueued]]] = {}

    def _reset_state(self) -> None:
        self._tracks = {}

    def _tracks_at(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: bool | None = None,
        waiting: bool | None = None,
    ) -> list[TrackQueued]:
        if date_ not in self._tracks:
            self._tracks[date_] = {}
        if break_ is not None and break_ not in self._tracks[date_]:
            self._tracks[date_][break_] = []

        tracks_on_date = self._tracks[date_]
        tracks = tracks_on_date
        if break_ is None:
            tracks_before_flattening = list(tracks_on_date.values())
            tracks = [track for lst in tracks_before_flattening for track in lst]
        else:
            tracks = tracks_on_date[break_]

        if played is not None:
            tracks = list(filter(lambda track: track.played is played, tracks))
        if waiting is not None:
            tracks = list(
                filter(
                    lambda track: track.waiting is waiting,
                    tracks,
                )
            )
        return tracks

    def get_track_on(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> Optional[TrackQueued]:
        matched = list(
            filter(
                lambda track: track.identity == identity, self._tracks_at(date_, break_)
            )
        )
        return matched[0] if len(matched) == 1 else None

    def get_all(
        self,
        date_: date,
        break_: Breaks | None = None,
        played: bool | None = None,
        waiting: bool | None = None,
    ) -> list[TrackQueued]:
        tracks = self._tracks_at(date_, break_, played=played, waiting=waiting)

        return tracks

    def count_on(
        self,
        date_: date,
        break_: Breaks | None = None,
        played: bool | None = None,
        waiting: bool | None = None,
    ) -> int:
        return len(
            self._tracks_at(
                date_,
                break_,
                played=played,
                waiting=waiting,
            )
        )

    def sum_durations_on(
        self,
        date_: date,
        break_: Breaks | None = None,
        played: bool | None = None,
        waiting: bool | None = None,
    ) -> Seconds:
        # tracks = self._tracks_at(
        #     date_,
        #     break_,
        #     played=played,
        #     waiting=waiting,
        # )
        # tracks_identities = [track.identity for track in tracks]
        # return Seconds(sum())
        raise NotImplementedError("Synek, joinów ci tutaj nie zrobię")

    def save(self, track: TrackQueued) -> TrackQueued:
        date_ = track.when.date_
        break_ = track.when.break_
        if len((self._tracks_at(date_, break_))) == 0:
            self._tracks[date_][break_].append(track)
            return track

        for idx, track_queued in enumerate(self._tracks_at(date_, break_)):
            if track_queued.identity == track.identity:
                self._tracks[date_][break_][idx] = track
        return track

    def delete(self, track: TrackQueued) -> TrackQueued:
        date_ = track.when.date_
        break_ = track.when.break_
        try:
            self._tracks[date_][break_].remove(track)
        except KeyError as ex:
            msg = "No queued track can be deleted as no one exists!"
            raise ValueError(msg) from ex
        else:
            return track
