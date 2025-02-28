from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from pytest import fixture

from building_blocks.clock import FixedClock
from config import BreakData, BreaksConfig
from domain.breaks import Break, Breaks
from domain.types import Seconds

_timezone = ZoneInfo("Europe/Warsaw")
_breaks_config = BreaksConfig(
    breaks=[
        BreakData(start=time(8, 30), duration=Seconds(10 * 60)),
        BreakData(start=time(9, 25), duration=Seconds(10 * 60)),
        BreakData(start=time(10, 20), duration=Seconds(10 * 60)),
        BreakData(start=time(11, 15), duration=Seconds(15 * 60)),
    ],
    offset=timedelta(seconds=Seconds(17)),
    timezone=_timezone,
)


@fixture
def during_first_break() -> Breaks:
    dt = datetime(2024, 8, 1, 8, 33, 54, tzinfo=_timezone)
    clock = FixedClock(dt)
    breaks_service = Breaks(config=_breaks_config, clock=clock)
    return breaks_service


@fixture
def after_first_break() -> Breaks:
    dt = datetime(2024, 8, 1, 8, 57, 17, tzinfo=_breaks_config.timezone)
    clock = FixedClock(dt)
    breaks_service = Breaks(config=_breaks_config, clock=clock)
    return breaks_service


@fixture
def after_last_break() -> Breaks:
    dt = datetime(2024, 8, 1, 17, 11, 56, tzinfo=_breaks_config.timezone)
    clock = FixedClock(dt)
    breaks_service = Breaks(config=_breaks_config, clock=clock)
    return breaks_service


def test_gets_breaks_as_list(during_first_break):
    breaks_list = during_first_break.as_list()
    assert len(breaks_list) == 4
    assert breaks_list[2] == Break(
        start=datetime(2024, 8, 1, 10, 20, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 1, 10, 30, 17, tzinfo=_timezone),
        ordinal=3,
    )


def test_gets_current_break(during_first_break):
    assert during_first_break.get_current() == Break(
        start=datetime(2024, 8, 1, 8, 30, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 1, 8, 40, 17, tzinfo=_timezone),
        ordinal=1,
    )


def test_gets_next_break_when_on_break(during_first_break):
    assert during_first_break.get_next() == Break(
        start=datetime(2024, 8, 1, 9, 25, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 1, 9, 35, 17, tzinfo=_timezone),
        ordinal=2,
    )


def test_gets_next_break_when_after_break(after_first_break):
    assert after_first_break.get_next() == Break(
        start=datetime(2024, 8, 1, 9, 25, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 1, 9, 35, 17, tzinfo=_timezone),
        ordinal=2,
    )


def test_gets_seconds_left_during_current_break(during_first_break):
    # (30 + 10 - 35) * 60 + (60 - 11) + offset
    assert during_first_break.get_seconds_left_during_current() == Seconds(366)


def test_gets_seconds_left_not_during_break(after_first_break):
    assert after_first_break.get_seconds_left_during_current() is None


def test_gets_remaining_time_to_next_break_during_break(during_first_break):
    assert during_first_break.get_remaining_time_to_next() == Seconds(45 * 60 + 366)


def test_gets_remaining_time_to_next_break_not_during_break(after_first_break):
    # (60 - 58 + 25) * 60 + (60 - 34) + offset
    assert after_first_break.get_remaining_time_to_next() == Seconds(1663)


def test_does_not_return_current_and_next_breaks_the_same_at_start():
    clock = FixedClock(datetime(2024, 8, 1, 8, 30, 0, tzinfo=_timezone))
    breaks_service = Breaks(config=_breaks_config, clock=clock)

    expected_break = Break(
        start=datetime(2024, 8, 1, 8, 30, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 1, 8, 40, 17, tzinfo=_timezone),
        ordinal=1,
    )
    assert breaks_service.get_current() == expected_break
    assert breaks_service.get_next() != expected_break


def test_does_not_return_current_and_next_breaks_the_same_at_end():
    clock = FixedClock(datetime(2024, 8, 1, 8, 40, 0, tzinfo=_timezone))
    breaks_service = Breaks(config=_breaks_config, clock=clock)

    expected_break = Break(
        start=datetime(2024, 8, 1, 8, 30, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 1, 8, 40, 17, tzinfo=_timezone),
        ordinal=1,
    )
    assert breaks_service.get_current() == expected_break
    assert breaks_service.get_next() != expected_break


def test_gets_next_break_tomorrow_when_after_last_break(after_last_break):
    assert after_last_break.get_next() == Break(
        start=datetime(2024, 8, 2, 8, 30, 17, tzinfo=_timezone),
        end=datetime(2024, 8, 2, 8, 40, 17, tzinfo=_timezone),
        ordinal=1,
    )
