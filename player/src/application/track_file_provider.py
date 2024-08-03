import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
import os
from pathlib import Path
from typing import Callable, Coroutine, Optional

from player.src.domain.breaks import Break, Seconds
from player.src.domain.track import Identifier, ScheduledTrack, TrackProvidedIdentity


@dataclass
class PlayableTrackProviderConfig:
    tracks_filepathdir: os.PathLike


@dataclass
class TrackToPlay:
    track: ScheduledTrack
    path: Path


class PlayableTrackProvider:
    def __init__(self, config: PlayableTrackProviderConfig) -> None:
        self._filepathdir = Path(config.tracks_filepathdir)
        self._track_to_play_misses = 0

        self._TEMP_podano = False

    def add_track_to_play_miss(self) -> None:
        self._track_to_play_misses = (self._track_to_play_misses + 1) % 6

    @property
    def wait_a_bit_on_track_to_play(self) -> Callable[[], Coroutine]:
        return lambda: asyncio.sleep(2**self._track_to_play_misses / 100)

    def _get_file_path_of(self, identity: TrackProvidedIdentity) -> Optional[Path]:
        filename = f"{identity.provider}_{identity.identifier}"
        path = self._filepathdir / filename
        if not path.exists():
            return None
        return path

    def get_track_to_play(self) -> Optional[TrackToPlay]:
        if self._TEMP_podano:
            return None
        self._TEMP_podano = True
        date_ = date(2024, 8, 3)
        break_ = Break(
            start=datetime.combine(date_, time(13, 15), tzinfo=timezone.utc),
            end=datetime.combine(date_, time(13, 25), tzinfo=timezone.utc),
            ordinal=4,
        )

        scheduled_track = ScheduledTrack(
            identity=TrackProvidedIdentity(
                identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
            ),
            break_=break_,
            duration=Seconds(42),
        )
        track_path = self._get_file_path_of(scheduled_track.identity)
        if track_path is None:
            raise RuntimeError("No track downloaded!")
            return None
        to_play = TrackToPlay(scheduled_track, track_path)
        return to_play
