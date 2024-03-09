from dataclasses import dataclass
from enum import IntEnum, auto, unique
from datetime import date, datetime, time


# Breaks = NewType("Breaks", dict[time, Seconds])
# DatabaseBreak = TypedDict(
#     "DatabaseBreak", {"type" = auto(), "startTime" = auto(), "duration": int}
# )


@unique
class BreaksEnum(IntEnum):
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
    break_: BreaksEnum

    def to_datetime(self) -> datetime:
        break_number = self.break_ - BreaksEnum.FIRST
        starting_time = list(Breaks._start_times.items())[break_number][0]
        return datetime.combine(self.date_, starting_time)

    # strefy czasowe trzeba obsługiwać
    def is_weekday(self) -> bool:
        return self.date_.isoweekday() > 5


class Breaks:
    _start_times = {
        time(8, 30): 10,
        time(9, 25): 10,
        time(10, 20): 10,
        time(11, 15): 15,
        time(12, 15): 10,
        time(13, 10): 10,
        time(14, 5): 10,
        time(15, 00): 10,
    }
