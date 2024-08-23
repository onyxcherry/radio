from typing import Annotated, Any
from pydantic import AwareDatetime, BeforeValidator, ConfigDict, Field, PlainSerializer
from pydantic.dataclasses import dataclass
from datetime import date, datetime, timezone

from player.src.domain.events.base import Event
from player.src.domain.entities import TrackProvidedIdentity


def millis_to_timestamp(v: Any) -> datetime:
    if isinstance(v, int):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
    return v


def ordinal_to_date(v: Any) -> date:
    if isinstance(v, int):
        return date.fromordinal(v)
    return v


MillisDatetime = Annotated[
    AwareDatetime,
    BeforeValidator(millis_to_timestamp),
    PlainSerializer(lambda dt: int(dt.timestamp() * 1000)),
]

OrdinalDate = Annotated[
    date, BeforeValidator(ordinal_to_date), PlainSerializer(lambda d: d.toordinal())
]

dataclass_config = ConfigDict(populate_by_name=True)


@dataclass(frozen=True, config=dataclass_config)
class PlayingTime:
    date_: OrdinalDate = Field(validation_alias="date", serialization_alias="date")
    break_: int = Field(validation_alias="break", serialization_alias="break")


@dataclass(frozen=True, config=dataclass_config)
class TrackAddedToPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    duration: int
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
