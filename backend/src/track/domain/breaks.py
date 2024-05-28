from dataclasses import dataclass
from enum import IntEnum, auto, unique
from datetime import date, datetime, time


BREAKS_START_TIMES = {
    time(8, 30): 10,
    time(9, 25): 10,
    time(10, 20): 10,
    time(11, 15): 15,
    time(12, 15): 10,
    time(13, 10): 10,
    time(14, 5): 10,
    time(15, 00): 10,
}


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


@dataclass(frozen=True)
class PlayingTime:
    date_: date
    break_: Breaks

    def to_datetime(self) -> datetime:
        break_number = self.break_ - Breaks.FIRST
        starting_time = list(BREAKS_START_TIMES.items())[break_number][0]
        return datetime.combine(self.date_, starting_time)

    def is_weekday(self) -> bool:
        return self.date_.isoweekday() > 5
