from dataclasses import dataclass, field
from datetime import datetime

from track.domain.events.base import Event
from track.domain.provided import TrackProvidedIdentity
from track.domain.entities import Status


@dataclass
class TrackAddedToLibrary(Event):
    name: str = field(default="TrackAddedToLibrary", init=False)
    identity: TrackProvidedIdentity
    created: datetime


@dataclass(frozen=True)
class TrackAccepted(Event):
    name: str = field(default="TrackAccepted", init=False)
    identity: TrackProvidedIdentity
    previous_status: Status
    created: datetime


@dataclass(frozen=True)
class TrackRejected(Event):
    name: str = field(default="TrackRejected", init=False)
    identity: TrackProvidedIdentity
    previous_status: Status
    created: datetime
