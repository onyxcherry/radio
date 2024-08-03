from abc import ABC, abstractmethod
from datetime import date, datetime, timezone


class Clock(ABC):
    @abstractmethod
    def get_current_date(self) -> date:
        pass

    @abstractmethod
    def now(self) -> datetime:
        pass

    @staticmethod
    def system_clock() -> "Clock":
        return SystemClock()

    @staticmethod
    def fixed_clock(date: datetime) -> "Clock":
        return FixedClock(date)


class SystemClock(Clock):
    def get_current_date(self) -> date:
        return datetime.now(timezone.utc).date()

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FixedClock(Clock):
    def __init__(self, at: datetime) -> None:
        self._at = at

    def get_current_date(self) -> date:
        return self._at.date()

    def now(self) -> datetime:
        return self._at
