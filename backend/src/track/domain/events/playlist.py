from pydantic.dataclasses import dataclass

from pydantic import ConfigDict, Field, PositiveInt

from track.domain.events.base import Event, MillisDatetime
from track.domain.provided import TrackProvidedIdentity
from track.domain.breaks import PlayingTime


dataclass_config = ConfigDict(populate_by_name=True)


@dataclass(frozen=True, config=dataclass_config)
class TrackAddedToPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    duration: PositiveInt
    waits_on_approval: bool
    created: MillisDatetime
    name: str = Field(
        default="TrackAddedToPlaylist", init=False, repr=False, alias="event_name"
    )


@dataclass(frozen=True, config=dataclass_config)
class TrackDeletedFromPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: MillisDatetime
    name: str = Field(
        default="TrackDeletedFromPlaylist", init=False, repr=False, alias="event_name"
    )


@dataclass(frozen=True, config=dataclass_config)
class TrackPlayed(Event):
    identity: TrackProvidedIdentity
    start: MillisDatetime
    end: MillisDatetime
    created: MillisDatetime
    break_: int = Field(validation_alias="break", serialization_alias="break")
    name: str = Field(default="TrackPlayed", init=False, repr=False, alias="event_name")


@dataclass(frozen=True, config=dataclass_config)
class TrackMarkedAsPlayed(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: MillisDatetime
    name: str = Field(
        default="TrackMarkedAsPlayed", init=False, repr=False, alias="event_name"
    )
