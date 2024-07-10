from dataclasses import dataclass
from datetime import datetime, timezone
from typing import ClassVar, Optional

from track.domain.provided import TrackProvidedIdentity
from track.domain.breaks import Breaks, PlayingTime
from track.domain.events_base import Serializable


@dataclass(frozen=True)
class TrackAddedToPlaylist(Serializable):
    identity: TrackProvidedIdentity
    when: PlayingTime
    waits_on_approval: bool
    created: Optional[datetime] = datetime.now(tz=timezone.utc)
    event_name: Optional[str] = "TrackAddedToPlaylist"


@dataclass(frozen=True)
class TrackDeletedFromPlaylist(Serializable):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: Optional[datetime] = datetime.now(tz=timezone.utc)


@dataclass(frozen=True)
class TrackPlayed(Serializable):
    identity: TrackProvidedIdentity
    break_: Breaks
    start: datetime
    end: datetime
    created: Optional[datetime] = datetime.now(tz=timezone.utc)


@dataclass(frozen=True)
class TrackMarkedAsPlayed(Serializable):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: Optional[datetime] = datetime.now(tz=timezone.utc)
