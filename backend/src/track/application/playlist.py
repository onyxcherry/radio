from datetime import date
from typing import Optional

from kink import inject
from building_blocks.clock import Clock
from track.application.interfaces.events import EventsConsumer, EventsProducer
from track.domain.events.playlist import (
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
    TrackMarkedAsPlayed,
)
from track.domain.entities import (
    TrackQueued,
    TrackRequested,
    TrackToQueue,
    TrackUnqueued,
)
from track.domain.breaks import Breaks, PlayingTime
from track.domain.playlist_repository import PlaylistRepository
from track.domain.provided import Seconds, TrackProvidedIdentity


@inject
class Playlist:
    _events_topic = "queue"

    # słuchanie eventu REJECTED - trzeba usunąć wszystkie z kolejek z każdego dnia
    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        events_producer: EventsProducer,
        events_consumer: EventsConsumer,
        clock: Clock,
    ):
        self._clock = clock
        self._playlist_repository = playlist_repository
        self._events_producer = events_producer
        self._events_consumer = events_consumer

    def get(
        self,
        identity: TrackProvidedIdentity,
        date_: date,
        break_: Optional[Breaks] = None,
    ) -> Optional[TrackQueued]:
        return self._playlist_repository.get_track_on(identity, date_, break_)

    def get_all(
        self,
        date_: date,
        break_: Optional[Breaks] = None,
        played: Optional[bool] = None,
        waiting: Optional[bool] = None,
    ) -> list[TrackQueued]:
        return self._playlist_repository.get_all(
            date_,
            break_,
            played,
            waiting,
        )

    def get_all_by_identity(self, identity: TrackProvidedIdentity) -> list[TrackQueued]:
        return self._playlist_repository.get_all_by_identity(identity)

    def add(self, req: TrackRequested) -> TrackQueued:
        to_save = TrackToQueue(
            req.identity,
            req.when,
            duration=req.duration,
            played=False,
        )
        already_added = self._playlist_repository.get_track_on(
            req.identity, req.when.date_, req.when.break_
        )
        if already_added is not None:
            return already_added
        saved = self._playlist_repository.insert(to_save)
        self._emit_update_event(saved)
        return saved

    def delete(self, track: TrackQueued) -> Optional[TrackQueued]:
        deleted = self._playlist_repository.delete(track)
        if deleted is not None:
            event = TrackDeletedFromPlaylist(
                deleted.identity, deleted.when, created=self._clock.now()
            )
            self._events_producer.produce(message=event)
        return deleted

    def delete_all_by(self, identity: TrackProvidedIdentity) -> list[TrackUnqueued]:
        deleted_list = self._playlist_repository.delete_all_with_identity(identity)
        now = self._clock.now()
        for track in deleted_list:
            event = TrackDeletedFromPlaylist(track.identity, track.when, created=now)
            self._events_producer.produce(message=event)
        return deleted_list

    def mark_as_played(self, track: TrackQueued) -> TrackQueued:
        to_save = track
        assert track.waiting is False
        to_save.played = True
        saved = self._playlist_repository.update(to_save)
        event = TrackMarkedAsPlayed(
            saved.identity, saved.when, created=self._clock.now()
        )
        self._events_producer.produce(message=event)
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

    def inform_update(self, identity: TrackProvidedIdentity) -> None:
        tracks = self.get_all_by_identity(identity)
        for track in tracks:
            self._emit_update_event(track)

    def _emit_update_event(self, track: TrackQueued) -> None:
        event = TrackAddedToPlaylist(
            track.identity,
            track.when,
            track.duration,
            track.waiting,
            created=self._clock.now(),
        )
        self._events_producer.produce(message=event)
