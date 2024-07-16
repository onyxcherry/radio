from dataclasses import dataclass, field
from datetime import datetime

from track.domain.events.base import Event
from track.domain.provided import TrackProvidedIdentity
from track.domain.breaks import Breaks, PlayingTime


@dataclass(frozen=True)
class TrackAddedToPlaylist(Event):
    name: str = field(default="TrackAddedToPlaylist", init=False, repr=False)
    identity: TrackProvidedIdentity
    when: PlayingTime
    waits_on_approval: bool
    created: datetime


@dataclass(frozen=True)
class TrackDeletedFromPlaylist(Event):
    name: str = field(default="TrackDeletedFromPlaylist", init=False, repr=False)
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: datetime


@dataclass(frozen=True)
class TrackPlayed(Event):
    name: str = field(default="TrackPlayed", init=False, repr=False)
    identity: TrackProvidedIdentity
    break_: Breaks
    start: datetime
    end: datetime
    created: datetime


@dataclass(frozen=True)
class TrackMarkedAsPlayed(Event):
    name: str = field(default="TrackMarkedAsPlayed", init=False, repr=False)
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: datetime
