import os
from pathlib import Path
import time
from typing import Callable, Optional

from player.src.domain.track import Seconds
from player.src.domain.interfaces.player import Player


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

    def play(
        self, duration: Seconds, callback_end: Optional[Callable[[], None]]
    ) -> None:
        self._playing = True
        print(f"Start playing: {self._filepath}", flush=True)
        # wait
        time.sleep(1)
        if callback_end is not None:
            callback_end()

    def stop(self) -> None:
        self._playing = False
        print(f"Stopped playing: {self._filepath}", flush=True)
