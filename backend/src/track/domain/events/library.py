from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from track.domain.provided import TrackProvidedIdentity
from track.domain.entities import Status
from track.domain.events_base import Serializable


@dataclass
class TrackAddedToLibrary(Serializable):
    identity: TrackProvidedIdentity
    created: Optional[datetime] = datetime.now(tz=timezone.utc)


@dataclass(frozen=True)
class TrackAccepted(Serializable):
    identity: TrackProvidedIdentity
    previous_status: Status
    created: Optional[datetime] = datetime.now(tz=timezone.utc)


@dataclass(frozen=True)
class TrackRejected(Serializable):
    identity: TrackProvidedIdentity
    previous_status: Status
    created: Optional[datetime] = datetime.now(tz=timezone.utc)
