from pydantic import Field
from pydantic.dataclasses import dataclass
from datetime import date, datetime

from player.src.domain.events.base import Event
from player.src.domain.entities import PlayingTime, TrackProvidedIdentity


@dataclass(frozen=True)
class TrackAddedToPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    waits_on_approval: bool
    created: datetime
    name: str = Field(default="TrackAddedToPlaylist", init=False, repr=False)


@dataclass(frozen=True)
class TrackDeletedFromPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: datetime
    name: str = Field(default="TrackDeletedFromPlaylist", init=False, repr=False)


@dataclass(frozen=True)
class TrackPlayed(Event):
    identity: TrackProvidedIdentity
    break_: int
    start: datetime
    end: datetime
    created: datetime
    name: str = Field(default="TrackPlayed", init=False, repr=False, alias="event_name")


@dataclass(frozen=True)
class TrackMarkedAsPlayed(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: datetime
    name: str = Field(default="TrackMarkedAsPlayed", init=False, repr=False)

