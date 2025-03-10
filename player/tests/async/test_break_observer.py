import asyncio
from datetime import datetime

import pytest
from kink import di

from application.break_observer import BreakObserver
from building_blocks.clock import FeignedWallClock
from config import BreaksConfig
from domain.breaks import Break, Breaks

breaks_config = di[BreaksConfig]


def get_break_observer(at: datetime) -> BreakObserver:
    clock = FeignedWallClock(at)
    breaks = Breaks(breaks_config, clock)
    break_observer = BreakObserver(breaks, clock)
    return break_observer


@pytest.fixture
def bo_before_start() -> BreakObserver:
    dt = datetime(2024, 8, 1, 8, 29, 59, 970000, tzinfo=breaks_config.timezone)
    return get_break_observer(dt)


@pytest.fixture
def bo_before_end() -> BreakObserver:
    dt = datetime(2024, 8, 1, 8, 39, 59, 800000, tzinfo=breaks_config.timezone)
    return get_break_observer(dt)


@pytest.mark.asyncio
async def test_observes_start_of_break(bo_before_start):
    assert bo_before_start.current is None
    task = asyncio.create_task(bo_before_start.update_current_break())
    await asyncio.sleep(0.01)

    assert bo_before_start.current is None
    await asyncio.sleep(0.1)

    assert bo_before_start.current is not None
    assert bo_before_start.current == Break(
        start=datetime(2024, 8, 1, 8, 30, 17, tzinfo=breaks_config.timezone),
        end=datetime(2024, 8, 1, 8, 40, 17, tzinfo=breaks_config.timezone),
        ordinal=1,
    )
    task.cancel()


@pytest.mark.asyncio
async def test_observes_end_of_break(bo_before_end):
    task = asyncio.create_task(bo_before_end.update_current_break())
    await asyncio.sleep(0.1)

    assert bo_before_end.current is not None
    assert bo_before_end.current == Break(
        start=datetime(2024, 8, 1, 8, 30, 17, tzinfo=breaks_config.timezone),
        end=datetime(2024, 8, 1, 8, 40, 17, tzinfo=breaks_config.timezone),
        ordinal=1,
    )
    await asyncio.sleep(0.2)

    assert bo_before_end.current is None
    task.cancel()
