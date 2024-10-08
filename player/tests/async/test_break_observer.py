import asyncio
from datetime import datetime
from kink import di
import pytest
from player.src.application.break_observer import BreakObserver
from player.src.building_blocks.clock import FeignedWallClock
from player.src.config import BreaksConfig
from player.src.domain.breaks import Break, Breaks
from player.src.domain.types import Seconds


breaks_config = di[BreaksConfig]


def get_break_observer(at: datetime) -> BreakObserver:
    breaks_config = di[BreaksConfig]
    clock = FeignedWallClock(at)
    breaks = Breaks(breaks_config, clock)
    break_observer = BreakObserver(breaks, clock)
    return break_observer


@pytest.fixture
def bo_before_start() -> BreakObserver:
    dt = datetime(2024, 8, 1, 8, 30, 6, 970000, tzinfo=breaks_config.timezone)
    return get_break_observer(dt)


@pytest.fixture
def bo_before_end() -> BreakObserver:
    dt = datetime(2024, 8, 1, 8, 30, 26, 800000, tzinfo=breaks_config.timezone)
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
        start=datetime(2024, 8, 1, 8, 30, 7, tzinfo=breaks_config.timezone),
        end=datetime(2024, 8, 1, 8, 30, 27, tzinfo=breaks_config.timezone),
        ordinal=0,
    )
    task.cancel()


@pytest.mark.asyncio
async def test_observes_end_of_break(bo_before_end):
    task = asyncio.create_task(bo_before_end.update_current_break())
    await asyncio.sleep(0.1)

    assert bo_before_end.current is not None
    assert bo_before_end.current == Break(
        start=datetime(2024, 8, 1, 8, 30, 7, tzinfo=breaks_config.timezone),
        end=datetime(2024, 8, 1, 8, 30, 27, tzinfo=breaks_config.timezone),
        ordinal=0,
    )
    await asyncio.sleep(0.2)

    assert bo_before_end.current is None
    task.cancel()
