from datetime import date
from pydantic import AwareDatetime
from pydantic.dataclasses import dataclass


from player.src.domain.breaks import Break
from player.src.domain.types import Identifier, ProviderName, Seconds


@dataclass(frozen=True)
class PlayingTime:
    date_: date
    break_: int


@dataclass(frozen=True, order=True)
class TrackProvidedIdentity:
    identifier: Identifier
    provider: ProviderName


@dataclass(frozen=True)
class TrackToSchedule:
    identity: TrackProvidedIdentity
    break_: Break
    duration: Seconds


@dataclass(frozen=True)
class ScheduledTrack:
    identity: TrackProvidedIdentity
    break_: Break
    duration: Seconds
    played: bool
    created: AwareDatetime
    last_changed: AwareDatetime
