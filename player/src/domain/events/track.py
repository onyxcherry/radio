from typing import Annotated, Any
from pydantic import AwareDatetime, BeforeValidator, ConfigDict, Field, PlainSerializer
from pydantic.dataclasses import dataclass
from datetime import datetime, timezone

from player.src.domain.events.base import Event
from player.src.domain.entities import PlayingTime, TrackProvidedIdentity


def millis_to_timestamp(v: Any) -> datetime:
    if isinstance(v, int):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
    return v


MillisDatetime = Annotated[
    AwareDatetime,
    BeforeValidator(millis_to_timestamp),
    PlainSerializer(lambda dt: int(dt.timestamp() * 1000)),
]

dataclass_config = ConfigDict(populate_by_name=True)


@dataclass(frozen=True, config=dataclass_config)
class TrackAddedToPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    waits_on_approval: bool
    created: MillisDatetime
    name: str = Field(default="TrackAddedToPlaylist", init=False, repr=False)


@dataclass(frozen=True, config=dataclass_config)
class TrackDeletedFromPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: MillisDatetime
    name: str = Field(default="TrackDeletedFromPlaylist", init=False, repr=False)


@dataclass(frozen=True, config=dataclass_config)
class TrackPlayed(Event):
    identity: TrackProvidedIdentity
    start: MillisDatetime
    end: MillisDatetime
    created: MillisDatetime
    break_: int = Field(validation_alias="break", serialization_alias="break")
    name: str = Field(default="TrackPlayed", init=False, repr=False, alias="event_name")


@dataclass(frozen=True, config=dataclass_config)
class TrackMarkedAsPlayed(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: MillisDatetime
    name: str = Field(default="TrackMarkedAsPlayed", init=False, repr=False)
