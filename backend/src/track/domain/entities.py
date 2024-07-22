from dataclasses import dataclass
from typing import Optional
from track.domain.breaks import PlayingTime

from track.domain.provided import (
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)

from enum import StrEnum, unique


@unique
class Status(StrEnum):
    ACCEPTED = "accepted"
    PENDING_APPROVAL = "pending"
    REJECTED = "rejected"

    def __repr__(self) -> str:
        return f"Status.{self.name}"


@dataclass
class TrackInLibrary:
    identity: TrackProvidedIdentity
    title: Optional[str]
    url: Optional[TrackUrl]
    duration: Optional[Seconds]
    status: Status


@dataclass(frozen=True)
class NewTrack:
    identity: TrackProvidedIdentity
    title: Optional[str]
    url: Optional[TrackUrl]
    duration: Optional[Seconds]


@dataclass
class TrackQueued:
    identity: TrackProvidedIdentity
    when: PlayingTime
    played: bool
    waiting: bool


@dataclass
class TrackUnqueued:
    identity: TrackProvidedIdentity
    when: PlayingTime


@dataclass
class TrackToQueue:
    identity: TrackProvidedIdentity
    when: PlayingTime
    played: bool


@dataclass(frozen=True)
class TrackRequested:
    identity: TrackProvidedIdentity
    when: PlayingTime
