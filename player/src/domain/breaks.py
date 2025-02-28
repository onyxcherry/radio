from datetime import date, datetime, timedelta
from typing import Optional, Self

from kink import inject
from pydantic import AwareDatetime, PositiveInt, model_validator
from pydantic.dataclasses import dataclass

from building_blocks.clock import Clock
from config import BreaksConfig, get_logger
from domain.types import Seconds


@dataclass(frozen=True)
class Break:
    start: AwareDatetime
    end: AwareDatetime
    ordinal: PositiveInt

    @model_validator(mode="after")
    def check_same_day(self) -> Self:
        if self.start.date() != self.end.date():
            raise ValueError("start and end dates are different days")
        return self

    @property
    def duration(self) -> Seconds:
        td = self.end - self.start
        return Seconds(int(td.total_seconds()))

    @property
    def date(self) -> date:
        return self.start.date()


logger = get_logger(__name__)


@inject
class Breaks:
    def __init__(self, config: BreaksConfig, clock: Clock) -> None:
        self._config = config
        self._clock = clock

    def _get_breaks(self, day: date) -> list[Break]:
        _breaks: list[Break] = []
        for idx, item in enumerate(self._config.breaks):
            start_datetime = (
                datetime.combine(day, item.start, tzinfo=self._config.timezone)
                + self._config.offset
            )
            if item.duration is None:
                raise RuntimeError(f"Duration is None of item: {item}")
            end_datetime = start_datetime + timedelta(seconds=item.duration)
            break_ = Break(start_datetime, end_datetime, idx + 1)
            _breaks.append(break_)
        return _breaks

    def as_list(self) -> list[Break]:
        return self.on_day(self._clock.get_current_date())

    def on_day(self, day: date) -> list[Break]:
        return self._get_breaks(day)

    def get_current(self) -> Optional[Break]:
        now = self._offsetted_now()
        for break_ in self.as_list():
            if break_.start <= now <= break_.end:
                return Break(break_.start, break_.end, break_.ordinal)
        return None

    def get_next(self) -> Break:
        return self._get_next_today() or self._get_tomorrow_first()

    def _get_next_today(self) -> Optional[Break]:
        now = self._offsetted_now()
        for break_ in self.as_list():
            if now < break_.start:
                return break_
        return None

    def _get_tomorrow_first(self) -> Break:
        tomorrow_breaks = self.on_day(
            self._clock.get_current_date() + timedelta(days=1)
        )
        return tomorrow_breaks[0]

    def get_remaining_time_to_next(self) -> Seconds:
        next_break = self.get_next()
        diff = next_break.start - self._offsetted_now()
        return Seconds(int(diff.total_seconds()))

    def get_seconds_left_during_current(self) -> Optional[Seconds]:
        current = self.get_current()
        if current is None:
            return None
        diff = current.end - self._offsetted_now()
        return Seconds(int(diff.total_seconds()))

    def on_day_of_ordinal(self, date_: date, ordinal: PositiveInt) -> Optional[Break]:
        breaks = self.on_day(date_)
        return breaks[ordinal - 1] if ordinal <= len(breaks) else None

    def _offsetted_now(self) -> datetime:
        return self._clock.now() + self._config.offset
