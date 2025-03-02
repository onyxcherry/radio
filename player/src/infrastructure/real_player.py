import array
import asyncio
import os
from typing import Callable, Generator, Optional, Union

import miniaudio

from config import get_logger
from domain.interfaces.player import Player
from domain.types import Seconds

logger = get_logger(__name__)


FramesType = Union[bytes, array.array]
PlaybackCallbackGeneratorType = Generator[FramesType, int, None]


class MiniaudioPlayer(Player):
    def __init__(self) -> None:
        self._playing = False
        self._filestream: Optional[PlaybackCallbackGeneratorType] = None
        self._fileinfo: Optional[miniaudio.SoundFileInfo] = None
        self._stop_event = asyncio.Event()

    def load_file(self, path: os.PathLike) -> None:
        fileinfo = miniaudio.get_file_info(str(path))
        filestream = miniaudio.stream_file(
            str(path),
            output_format=fileinfo.sample_format,
            sample_rate=fileinfo.sample_rate,
        )
        # TODO: handle miniaudio.MiniaudioError in recoverable way
        self._fileinfo = fileinfo
        self._filestream = filestream

    @property
    def playing(self) -> bool:
        return self._playing

    async def play(
        self, duration: Seconds, callback_end: Optional[Callable[[], None]]
    ) -> None:
        assert self._fileinfo is not None
        assert self._filestream is not None
        file_duration = int(self._fileinfo.duration)
        real_duration = int(duration)
        if file_duration < duration:
            logger.warning(
                f"Real duration ({file_duration}s) of loaded track is lower "
                f"than expected: {duration}s"
            )
            real_duration = file_duration
        stream = self._stream_n_seconds(
            self._filestream,
            Seconds(real_duration),
            self._fileinfo.sample_rate,
        )
        next(stream)
        with miniaudio.PlaybackDevice(
            output_format=self._fileinfo.sample_format,
            sample_rate=self._fileinfo.sample_rate,
        ) as device:
            device.start(stream)
            try:
                await asyncio.wait_for(self._stop_event.wait(), real_duration)
            except TimeoutError:
                logger.info("Playing has stopped - played full duration")
            else:
                logger.info("Playing has stopped due to stop() called")
        if callback_end is not None:
            callback_end()

    def stop(self, force=False) -> None:
        self._stop_event.set()

    def _stream_n_seconds(
        self,
        sample_stream: PlaybackCallbackGeneratorType,
        seconds: Seconds,
        sample_rate: int,
    ) -> PlaybackCallbackGeneratorType:
        frames_to_play = sample_rate * seconds
        frames_yielded = 0
        frame_count = yield b""
        try:
            while frames_yielded + frame_count <= frames_to_play:
                frame = sample_stream.send(frame_count)
                frame_count = yield frame
                frames_yielded += frame_count
        except StopIteration:
            pass
