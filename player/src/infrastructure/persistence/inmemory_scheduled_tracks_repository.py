from datetime import date
from typing import Optional

from building_blocks.clock import Clock
from domain.breaks import Break
from domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
)
from domain.events.compare import events_differ_only_last_changed
from domain.repositories.scheduled_tracks import ScheduledTracksRepository


class InMemoryScheduledTracksRepository(ScheduledTracksRepository):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._tracks: dict[date, dict[int, list[ScheduledTrack]]] = {}

    def _tracks_at(
        self,
        date_: date,
        break_: Optional[int] = None,
        played: Optional[bool] = None,
    ) -> list[ScheduledTrack]:
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
        return tracks

    def get_track_on(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[int] = None,
    ) -> Optional[ScheduledTrack]:
        tracks = self._tracks_at(date_, break_)
        matched = list(filter(lambda track: track.identity == identity, tracks))
        return matched[0] if len(matched) == 1 else None

    def get_all(
        self,
        date_: date,
        break_: Optional[int] = None,
        played: Optional[bool] = None,
    ) -> list[ScheduledTrack]:
        tracks = sorted(
            self._tracks_at(date_, break_, played=played),
            key=lambda x: (x.break_.ordinal, x.created, x.identity),
        )

        return tracks

    def insert(self, track: TrackToSchedule) -> ScheduledTrack:
        already_scheduled = self.get_track_on(
            identity=track.identity,
            date_=track.break_.date,
            break_=track.break_.ordinal,
        )
        if already_scheduled is not None:
            return already_scheduled

        date_ = track.break_.start.date()
        break_ = track.break_
        now = self._clock.now()
        scheduled = ScheduledTrack(
            identity=track.identity,
            break_=break_,
            duration=track.duration,
            played=False,
            created=now,
            last_changed=now,
        )
        self._tracks_at(date_, break_.ordinal)
        self._tracks[date_][break_.ordinal].append(scheduled)
        return scheduled

    def update(self, track: ScheduledTrack) -> ScheduledTrack:
        date_ = track.break_.date
        break_ = track.break_

        for idx, track_queued in enumerate(self._tracks_at(date_, break_.ordinal)):
            if track_queued.identity == track.identity and track_queued.played is False:
                scheduled = ScheduledTrack(
                    identity=track.identity,
                    break_=break_,
                    duration=track.duration,
                    played=track.played,
                    created=track_queued.created,
                    last_changed=self._clock.now(),
                )
                if not events_differ_only_last_changed(track_queued, scheduled):
                    self._tracks[date_][break_.ordinal][idx] = scheduled
        return scheduled

    def insert_or_update(
        self, track: TrackToSchedule | ScheduledTrack
    ) -> ScheduledTrack:
        already_scheduled_track = self.get_track_on(
            track.identity, track.break_.date, track.break_.ordinal
        )
        if already_scheduled_track is None:
            to_scheduled = TrackToSchedule(
                identity=track.identity, break_=track.break_, duration=track.duration
            )
            return self.insert(to_scheduled)

        if isinstance(track, TrackToSchedule):
            scheduled = ScheduledTrack(
                identity=track.identity,
                break_=track.break_,
                duration=track.duration,
                played=already_scheduled_track.played,
                created=already_scheduled_track.created,
                last_changed=already_scheduled_track.last_changed,
            )
            return self.update(scheduled)
        return self.update(track)

    def delete(self, track: ScheduledTrack) -> Optional[ScheduledTrack]:
        date_ = track.break_.start.date()
        break_ = track.break_
        if track.played is True:
            return None
        try:
            self._tracks[date_][break_.ordinal].remove(track)
        except KeyError as ex:
            msg = "No scheduled track can be deleted as no one exists!"
            raise ValueError(msg) from ex
        else:
            return track

    def delete_all(self) -> int:
        removed: list[ScheduledTrack] = []
        for breaks_with_scheduled in list(self._tracks.values()):
            for track_list in list(breaks_with_scheduled.values()):
                removed += track_list
        self._tracks = {}
        return len(removed)

    def delete_all_with_identity(self, identity: TrackProvidedIdentity) -> int:
        removed: list[ScheduledTrack] = []

        for breaks_with_queued in list(self._tracks.values()):
            for break_key, track_list in list(breaks_with_queued.items()):
                filtered: list[ScheduledTrack] = []
                for track in track_list:
                    if track.identity == identity and track.played is False:
                        removed.append(track)
                    else:
                        filtered.append(track)
                breaks_with_queued[break_key] = filtered
        return len(removed)
