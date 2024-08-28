from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from track.domain.events.base import Event, MillisDatetime
from track.domain.provided import TrackProvidedIdentity
from track.domain.entities import Status

dataclass_config = ConfigDict(populate_by_name=True)


@dataclass
class TrackAddedToLibrary(Event):
    identity: TrackProvidedIdentity
    created: MillisDatetime
    name: str = Field(
        default="TrackAddedToLibrary", init=False, repr=False, alias="event_name"
    )


@dataclass(frozen=True)
class TrackAccepted(Event):
    identity: TrackProvidedIdentity
    previous_status: Status
    created: MillisDatetime
    name: str = Field(
        default="TrackAccepted", init=False, repr=False, alias="event_name"
    )


@dataclass(frozen=True)
class TrackRejected(Event):
    identity: TrackProvidedIdentity
    previous_status: Status
    created: MillisDatetime
    name: str = Field(
        default="TrackRejected", init=False, repr=False, alias="event_name"
    )
