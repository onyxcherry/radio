import asyncio
from typing import Callable, Coroutine, Never, Optional

from kink import di, inject

from player.src.building_blocks.clock import Clock
from player.src.config import get_logger
from player.src.domain.breaks import Break, Breaks
from player.src.domain.interfaces.player import Player
from player.src.domain.types import Seconds

logger = get_logger(__name__)


@inject
class BreakObserver:
    def __init__(self, breaks: Breaks, clock: Clock) -> None:
        self._clock = clock
        self._breaks = breaks
        self._event = asyncio.Event()
        # defaults to no-break state as it is safer
        # self._event.set()
        self._current: Optional[Break] = None
        self._seconds_left: Seconds = Seconds(0)

    async def create_task(self) -> asyncio.Task:
        self._updating_task = asyncio.create_task(self.update_current_break())
        return self._updating_task

    @property
    def current(self) -> Optional[Break]:
        return self._current

    @property
    def seconds_left(self) -> Seconds:
        return self._seconds_left

    @property
    def wait_next(self) -> Callable[[], Coroutine]:
        return self._event.wait

    def reload_breaks(self) -> None: ...

    async def update_current_break(self) -> Never:
        logger.info("Started updating current breaks")
        player = di[Player]
        _waiting_noop_time = 0.01

        while True:
            current = self._breaks.get_current()
            if current is not None:
                self._current = current
                self._event.set()
                seconds_left = self._breaks.get_seconds_left_during_current()
                self._seconds_left = seconds_left or Seconds(0)
                logger.debug(f"{self._seconds_left=}")
                await asyncio.sleep(max(self._seconds_left, _waiting_noop_time))
            else:
                self._current = None
                self._event.clear()
                seconds_to_next = self._breaks.get_remaining_time_to_next()
                logger.debug(f"{seconds_to_next=}")
                player.stop(force=True)
                await asyncio.sleep(max(seconds_to_next, _waiting_noop_time))
