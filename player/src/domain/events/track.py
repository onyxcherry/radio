from dataclasses import dataclass
from datetime import datetime

from player.src.domain.track import TrackProvidedIdentity


class Event:
    pass


@dataclass(frozen=True)
class TrackPlayed(Event):
    identity: TrackProvidedIdentity
    break_: int
    start: datetime
    end: datetime
