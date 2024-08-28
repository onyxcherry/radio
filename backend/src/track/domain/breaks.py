from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
from enum import IntEnum, auto, unique
from datetime import date, datetime, time, timezone

from backend.src.track.domain.events.base import DateFromUnixEpoch
from track.domain.provided import Seconds

dataclass_config = ConfigDict(populate_by_name=True)


_BREAKS_START_TIMES = {
    time(8, 30): Seconds(10 * 60),
    time(9, 25): Seconds(10 * 60),
    time(10, 20): Seconds(10 * 60),
    time(11, 15): Seconds(15 * 60),
    time(12, 15): Seconds(10 * 60),
    time(13, 10): Seconds(10 * 60),
    time(14, 5): Seconds(10 * 60),
    time(15, 00): Seconds(10 * 60),
}


def get_breaks_starting_times():
    return list(_BREAKS_START_TIMES.keys())


def get_breaks_durations():
    return list(_BREAKS_START_TIMES.values())


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

    def to_datetime(self) -> datetime:
        break_number = self.break_.get_number_from_zero_of()
        starting_time = get_breaks_starting_times()[break_number]
        return datetime.combine(self.date_, starting_time, tzinfo=timezone.utc)

    def is_on_weekend(self) -> bool:
        return self.date_.isoweekday() > 5
