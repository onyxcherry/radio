from copy import deepcopy
from dataclasses import dataclass
from typing import Optional
from kink import inject
from building_blocks.clock import Clock
from track.application.interfaces.events import EventsProducer
from track.domain.events.library import (
    TrackAccepted,
    TrackAddedToLibrary,
    TrackRejected,
)
from track.domain.entities import NewTrack, Status, TrackInLibrary
from track.domain.library_repository import LibraryRepository
from track.domain.provided import TrackProvidedIdentity


@dataclass
class _ChangeStatusResult:
    previous: TrackInLibrary
    current: TrackInLibrary


@inject
class Library:
    _events_topic = "library"

    def __init__(
        self,
        library_repository: LibraryRepository,
        events_producer: EventsProducer,
        clock: Clock,
    ):
        self._clock = clock
        self._library_repository = library_repository
        self._events_producer = events_producer

    def filter_by_statuses(
        self,
        statuses: list[Status],
    ) -> list[TrackInLibrary]:
        return self._library_repository.filter_by_statuses(statuses)

    def get(self, identity: TrackProvidedIdentity) -> Optional[TrackInLibrary]:
        return self._library_repository.get(identity=identity)

    def add(self, track: NewTrack):
        default_status = Status.PENDING_APPROVAL
        track_to_add = TrackInLibrary(
            identity=track.identity,
            title=track.title,
            url=track.url,
            duration=track.duration,
            status=default_status,
        )
        self._library_repository.add(track_to_add)
        event = TrackAddedToLibrary(track.identity, created=self._clock.now())
        self._events_producer.produce(message=event)

    def _change_status(
        self, identity: TrackProvidedIdentity, status: Status
    ) -> _ChangeStatusResult:
        track = self._library_repository.get(identity)
        if track is None:
            raise RuntimeError("No track with given identity")
        old_track = deepcopy(track)
        track.status = status
        new_track = self._library_repository.update(track)
        return _ChangeStatusResult(previous=old_track, current=new_track)

    def accept(self, identity: TrackProvidedIdentity) -> TrackInLibrary:
        new_status = Status.ACCEPTED
        result = self._change_status(identity, new_status)
        event = TrackAccepted(
            identity, previous_status=result.previous.status, created=self._clock.now()
        )
        self._events_producer.produce(message=event)
        return result.current

    def reject(self, identity: TrackProvidedIdentity) -> TrackInLibrary:
        new_status = Status.REJECTED
        result = self._change_status(identity, new_status)
        event = TrackRejected(
            identity, previous_status=result.previous.status, created=self._clock.now()
        )
        self._events_producer.produce(message=event)
        return result.current
