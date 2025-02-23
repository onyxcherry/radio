import asyncio
import os
from pathlib import Path
import time
from typing import Callable, Optional

from config import get_logger
from domain.types import Seconds
from domain.interfaces.player import Player


logger = get_logger(__name__)


class MadeupPlayer(Player):
    def __init__(self) -> None:
        self._playing = False
        self._filepath: Optional[os.PathLike] = None

    def load_file(self, path: os.PathLike) -> None:
        if not Path(path).exists():
            raise RuntimeError(f"Path {path} not exist!")
        self._filepath = path

    @property
    def playing(self) -> bool:
        return self._playing

    async def play(
        self, duration: Seconds, callback_end: Optional[Callable[[], None]]
    ) -> None:
        self._playing = True
        logger.info(f"Start playing: {self._filepath}")
        await asyncio.sleep(duration)
        if callback_end is not None:
            callback_end()

    def stop(self, force=False) -> None:
        if force is True and self._playing:
            logger.error("Music is playing but should have had been stopped!")
            logger.warning("Stopping")
        self._playing = False
        logger.info(f"Stopped playing: {self._filepath}")
