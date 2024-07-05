from dataclasses import dataclass
from typing import Optional
from track.domain.breaks import PlayingTime

from track.domain.provided import (
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)

from enum import Enum, unique


@unique
class Status(Enum):
    ACCEPTED = "accepted"
    PENDING_APPROVAL = "pending"
    REJECTED = "rejected"


@dataclass
class TrackInLibrary:
    identity: TrackProvidedIdentity
    title: str
    url: TrackUrl
    duration: Seconds
    status: Status


@dataclass(frozen=True)
class NewTrack:
    identity: TrackProvidedIdentity
    title: str
    url: TrackUrl
    duration: Seconds


@dataclass
class TrackQueued:
    identity: TrackProvidedIdentity
    when: PlayingTime
    played: bool
    waiting: bool


@dataclass
class TrackToQueue:
    identity: TrackProvidedIdentity
    when: PlayingTime
    played: bool


@dataclass(frozen=True)
class TrackRequested:
    identity: TrackProvidedIdentity
    when: PlayingTime
