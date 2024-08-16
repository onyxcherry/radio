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


class FeignedWallClock(Clock):
    def __init__(self, feigned_dt: datetime) -> None:
        now = datetime.now(tz=timezone.utc)
        if feigned_dt.tzinfo is None:
            raise RuntimeError("Timezone for this feigned datetime cannot be empty!")
        self._time_shift = feigned_dt - now

    def get_current_date(self) -> date:
        return self.now().date()

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + self._time_shift


class FixedClock(Clock):
    def __init__(self, at: datetime) -> None:
        self._at = at

    def get_current_date(self) -> date:
        return self._at.date()

    def now(self) -> datetime:
        return self._at

    def __str__(self):
        return f"FixedClock(at={self._at!s})"

    def __repr__(self):
        return f"FixedClock(at={self._at!r})"
