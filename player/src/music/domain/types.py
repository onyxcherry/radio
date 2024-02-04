from dataclasses import dataclass
from datetime import datetime, time
from typing import Final, Literal, NewType, Union

from track.types import TrackUrl
from typing_extensions import NotRequired, TypedDict

NoTrackPlaying = NewType("NoTrackPlaying", str)
DB_PLAYER_QUERY: Final = {"type": "player"}


@dataclass
class TrackPlaying:
    url: TrackUrl
    when: datetime

    def __str__(self):
        return f"<Scheduled playing {self.url} at {self.when}>"

    def __repr__(self):
        return f"<TrackPlaying url={self.url} when={self.when}>"


class PlayerStatusData(TypedDict, total=True):
    errorOccured: bool
    manuallyStopped: bool
    trackUrl: TrackUrl | NoTrackPlaying


class PlayerStatusUpdate(TypedDict, total=False):
    duringBreak: bool
    errorOccured: bool
    manuallyStopped: bool
    trackUrl: TrackUrl | NoTrackPlaying
    title: NotRequired[str]


class _PlayerStatusStoppedResp(PlayerStatusData, total=True):
    stopped: Literal[True]
    reason: str
    duringBreak: NotRequired[bool]


class _PlayerStatusNotStoppedResp(PlayerStatusData, total=True):
    stopped: Literal[False]
    title: str
    duringBreak: bool


PlayerStatusResponse = Union[_PlayerStatusStoppedResp, _PlayerStatusNotStoppedResp]
