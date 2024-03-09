from dataclasses import dataclass
from track.domain.breaks import PlayingTime

from track.domain.status import Status
from track.domain.track import Seconds, TrackUrl


@dataclass
class TrackEntity:
    title: str
    url: TrackUrl
    duration: Seconds
    status: Status
    ready: bool


@dataclass(frozen=True)
class TrackRequestedAt:
    url: TrackUrl
    when: PlayingTime


@dataclass(frozen=True)
class TrackQueued:
    url: TrackUrl
    when: PlayingTime
    waiting: bool


@dataclass(frozen=True)
class NewTrack:
    title: str
    url: TrackUrl
    duration: Seconds
