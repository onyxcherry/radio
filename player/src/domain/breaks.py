from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional

from kink import inject


from player.src.building_blocks.clock import Clock
from player.src.config import BreaksConfig, get_logger
from player.src.domain.types import Seconds


@dataclass(frozen=True)
class Break:
    start: datetime
    end: datetime  # check if same date as start
    ordinal: int

    @property
    def duration(self) -> Seconds:
        return Seconds((self.end - self.start).seconds)


logger = get_logger(__name__)


@inject
class Breaks:
    def __init__(self, config: BreaksConfig, clock: Clock) -> None:
        self._config = config
        self._clock = clock
        self._today = self._clock.get_current_date()
        self._breaks = self._get_breaks(self._today)

    def _get_breaks(self, today: date) -> list[Break]:
        _breaks: list[Break] = []
        for idx, item in enumerate(self._config.start_times.items()):
            start_time, dur = item
            start_datetime = (
                datetime.combine(today, start_time, tzinfo=self._config.timezone)
                + self._config.offset
            )
            end_datetime = start_datetime + timedelta(seconds=dur)
            break_ = Break(start_datetime, end_datetime, idx)
            _breaks.append(break_)
        return _breaks

    def as_list(self) -> list[Break]:
        return self._breaks

    def get_current(self) -> Optional[Break]:
        now = self._clock.now()
        for break_ in self.as_list():
            if break_.start <= now <= break_.end:
                return Break(break_.start, break_.end, break_.ordinal)
        return None

    def get_next_today(self) -> Optional[Break]:
        now = self._clock.now()
        for break_ in self.as_list():
            if now < break_.start:
                return break_
        return None

    def get_next(self) -> Break:
        return self.get_next_today() or self._get_tomorrow_first()

    def get_next_after(self, ordinal: int, today=True) -> Optional[Break]:
        for current, next_ in zip(self._breaks, self._breaks[1:]):
            if current.ordinal == ordinal:
                return next_
        if today:
            return None
        else:
            return self._get_tomorrow_first()

    def _get_tomorrow_first(self) -> Break:
        tomorrow_dt = self.as_list()[0].start + timedelta(days=1)
        tomorrow = tomorrow_dt.date()
        tomorrow_first_break = self._get_breaks(tomorrow)[0]
        return tomorrow_first_break

    def get_remaining_time_to_next(self) -> Seconds:
        next_ = self.get_next()
        if next_ is None:
            raise RuntimeError()
        logger.debug(f"{next_=}")
        diff = next_.start - self._clock.now()
        return Seconds(diff.seconds)

    def get_seconds_left_during_current(self) -> Optional[Seconds]:
        current = self.get_current()
        if current is None:
            return None
        diff = current.end - self._clock.now()
        return Seconds(diff.seconds)
