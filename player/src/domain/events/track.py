from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Any

from pydantic import (
    AwareDatetime,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    PositiveInt,
)
from pydantic.dataclasses import dataclass

from domain.entities import TrackProvidedIdentity
from domain.events.base import Event


def datetime_as_millis_timestamp(data, *args) -> int:
    if isinstance(data, int):
        return data
    dt = data
    if not isinstance(dt, datetime):
        dt = datetime.fromisoformat(dt)
    return int(dt.timestamp() * 1000)


def millis_timestamp_as_datetime(v: Any, *args) -> datetime:
    if isinstance(v, int):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
    return v


def date_as_unix_epoch_date_int(data, *args) -> int:
    if isinstance(data, int):
        return data
    return (data - date(1970, 1, 1)).days


def unix_epoch_date_int_as_date(v: Any, *args) -> date:
    if isinstance(v, int):
        return date(1970, 1, 1) + timedelta(days=v)
    return v


MillisDatetime = Annotated[
    AwareDatetime,
    BeforeValidator(millis_timestamp_as_datetime),
    PlainSerializer(datetime_as_millis_timestamp),
]

DateFromUnixEpoch = Annotated[
    date,
    BeforeValidator(unix_epoch_date_int_as_date),
    PlainSerializer(date_as_unix_epoch_date_int),
]

dataclass_config = ConfigDict(populate_by_name=True)


@dataclass(frozen=True, config=dataclass_config)
class PlayingTime:
    date_: DateFromUnixEpoch = Field(
        validation_alias="date", serialization_alias="date"
    )
    break_: PositiveInt = Field(validation_alias="break", serialization_alias="break")


@dataclass(frozen=True, config=dataclass_config)
class TrackAddedToPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    duration: PositiveInt
    waits_on_approval: bool
    created: MillisDatetime
    name: str = Field(
        default="TrackAddedToPlaylist", init=False, repr=False, alias="event_name"
    )


@dataclass(frozen=True, config=dataclass_config)
class TrackDeletedFromPlaylist(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: MillisDatetime
    name: str = Field(
        default="TrackDeletedFromPlaylist", init=False, repr=False, alias="event_name"
    )


@dataclass(frozen=True, config=dataclass_config)
class TrackPlayed(Event):
    identity: TrackProvidedIdentity
    start: MillisDatetime
    end: MillisDatetime
    created: MillisDatetime
    break_: PositiveInt = Field(validation_alias="break", serialization_alias="break")
    name: str = Field(default="TrackPlayed", init=False, repr=False, alias="event_name")


@dataclass(frozen=True, config=dataclass_config)
class TrackMarkedAsPlayed(Event):
    identity: TrackProvidedIdentity
    when: PlayingTime
    created: MillisDatetime
    name: str = Field(
        default="TrackMarkedAsPlayed", init=False, repr=False, alias="event_name"
    )
