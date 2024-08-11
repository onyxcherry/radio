import asyncio
from pydantic.dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, Coroutine, Optional

from player.src.building_blocks.clock import Clock
from player.src.domain.entities import ScheduledTrack, TrackProvidedIdentity
from player.src.config import get_logger
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository


@dataclass(frozen=True)
class PlayableTrackProviderConfig:
    tracks_filepathdir: os.PathLike


@dataclass(frozen=True)
class TrackToPlay:
    track: ScheduledTrack
    path: Path


logger = get_logger(__name__)


class PlayableTrackProvider:
    def __init__(
        self,
        config: PlayableTrackProviderConfig,
        scheduled_tracks_repo: ScheduledTracksRepository,
        clock: Clock,
    ) -> None:
        self._filepathdir = Path(config.tracks_filepathdir)
        self._scheduled_tracks_repo = scheduled_tracks_repo
        self._clock = clock
        self._track_to_play_misses = 0

    def add_track_to_play_miss(self) -> None:
        self._track_to_play_misses = (self._track_to_play_misses + 1) % 6

    @property
    def wait_a_bit_on_track_to_play(self) -> Callable[[], Coroutine]:
        waiting_time = 2**self._track_to_play_misses / 100
        logger.debug(f"Will wait {waiting_time} seconds")
        return lambda: asyncio.sleep(waiting_time)

    def _get_file_path_of(self, identity: TrackProvidedIdentity) -> Optional[Path]:
        filename = f"{identity.provider}_{identity.identifier}"
        path = self._filepathdir / filename
        if not path.exists():
            return None
        return path

    def get_track_to_play(self) -> Optional[TrackToPlay]:
        date_ = self._clock.get_current_date()
        scheduled_tracks = self._scheduled_tracks_repo.get_all(
            date_=date_, played=False
        )
        if len(scheduled_tracks) == 0:
            return None

        scheduled_track = scheduled_tracks[0]
        track_path = self._get_file_path_of(scheduled_track.identity)
        if track_path is None:
            raise RuntimeError("No track downloaded!")
        to_play = TrackToPlay(scheduled_track, track_path)
        return to_play
