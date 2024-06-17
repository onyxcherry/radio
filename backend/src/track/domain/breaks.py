from dataclasses import dataclass
from enum import IntEnum, auto, unique
from datetime import date, datetime, time, timezone


_BREAKS_START_TIMES = {
    time(8, 30): 10,
    time(9, 25): 10,
    time(10, 20): 10,
    time(11, 15): 15,
    time(12, 15): 10,
    time(13, 10): 10,
    time(14, 5): 10,
    time(15, 00): 10,
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


@dataclass(frozen=True)
class PlayingTime:
    date_: date
    break_: Breaks

    def to_datetime(self) -> datetime:
        break_number = self.break_.get_number_from_zero_of()
        starting_time = get_breaks_starting_times()[break_number]
        return datetime.combine(self.date_, starting_time, tzinfo=timezone.utc)

    def is_on_weekend(self) -> bool:
        return self.date_.isoweekday() > 5
