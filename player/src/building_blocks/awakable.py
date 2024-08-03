import asyncio
from typing import Callable, Coroutine


class EventBasedAwakable:
    def __init__(self) -> None:
        self._event = asyncio.Event()
        self._event.set()

    def will_wait(self) -> bool:
        return not self._event.is_set()

    @property
    def wait_for(self) -> Callable[[], Coroutine]:
        return self._event.wait

    def awake(self) -> None:
        self._event.set()

    def sleep_again(self) -> None:
        self._event.clear()
