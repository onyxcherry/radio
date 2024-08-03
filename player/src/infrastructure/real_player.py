import os
from typing import Callable, Optional
from just_playback import Playback

from player.src.domain.track import Seconds
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

    def play(
        self, duration: Seconds, callback_end: Optional[Callable[[], None]]
    ) -> None:
        # TODO: play no more than `duration` seconds!!
        self._playback.play()
        if callback_end is not None:
            callback_end()

    def stop(self) -> None:
        self._playback.stop()
