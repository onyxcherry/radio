import os
from abc import abstractmethod
from typing import Callable, Optional

from domain.breaks import Seconds


class Player:
    @abstractmethod
    def load_file(self, path: os.PathLike) -> None:
        pass

    @property
    @abstractmethod
    def playing(self) -> bool:
        pass

    @abstractmethod
    async def play(
        self, duration: Seconds, callback_end: Optional[Callable[[], None]]
    ) -> None:
        pass

    @abstractmethod
    def stop(self, force=False) -> None:
        pass
