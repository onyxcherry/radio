from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
from enum import IntEnum, auto, unique
from datetime import date, datetime, time, timezone

from track.domain.events.base import DateFromUnixEpoch
from track.domain.provided import Seconds

dataclass_config = ConfigDict(populate_by_name=True)


@unique
class Breaks(IntEnum):
    FIRST = auto()
    SECOND = auto()
    THIRD = auto()
    FOURTH = auto()
    FIFTH = auto()
    SIXTH = auto()
    SEVENTH = auto()
    EIGHTH = auto()

    def get_number_from_zero_of(self) -> int:
        return self - self.FIRST

    def __repr__(self) -> str:
        return f"Breaks.{self.name}"


@dataclass(frozen=True, config=dataclass_config)
class PlayingTime:
    date_: DateFromUnixEpoch = Field(
        validation_alias="date", serialization_alias="date"
    )
    break_: Breaks = Field(validation_alias="break", serialization_alias="break")

    def is_on_weekend(self) -> bool:
        return self.date_.isoweekday() > 5
