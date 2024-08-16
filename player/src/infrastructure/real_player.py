import os
from typing import Callable, Optional
from just_playback import Playback

from player.src.domain.types import Seconds
from player.src.domain.interfaces.player import Player


class JustPlaybackPlayer(Player):
    def __init__(self) -> None:
        self._playback = Playback()

    def load_file(self, path: os.PathLike) -> None:
        if not isinstance(path, str):
            path_str = str(path)
        self._playback.load_file(path_str)

    @property
    def playing(self) -> bool:
        return self._playback.playing

    async def play(
        self, duration: Seconds, callback_end: Optional[Callable[[], None]]
    ) -> None:
        # TODO: play no more than `duration` seconds!!
        # loop.call_at can schedule .stop() call
        # https://docs.python.org/3/library/asyncio-eventloop.html#scheduling-delayed-callbacks
        self._playback.play()
        if callback_end is not None:
            callback_end()

    def stop(self) -> None:
        self._playback.stop()
