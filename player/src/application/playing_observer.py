import asyncio
from datetime import datetime
from typing import Callable, Coroutine, Optional

from kink import di
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository
from player.src.infrastructure.messaging.types import PlaylistEventsProducer
from player.src.config import get_logger

from player.src.building_blocks.clock import Clock
from player.src.domain.breaks import Break, Breaks
from player.src.domain.entities import ScheduledTrack
from player.src.domain.events.track import TrackPlayed
from player.src.domain.types import Seconds

logger = get_logger(__name__)

playlist_producer = di[PlaylistEventsProducer]


class PlayingObserver:
    def __init__(
        self,
        breaks: Breaks,
        scheduled_tracks_repo: ScheduledTracksRepository,
        clock: Clock,
    ) -> None:
        self._breaks = breaks
        self._scheduled_tracks_repo = scheduled_tracks_repo
        self._clock = clock
        self._track_playing_event = asyncio.Event()
        self._get_track_to_play_event = asyncio.Event()
        self._currently_playing: Optional[ScheduledTrack] = None
        self._start_playing_dt: Optional[datetime] = None
        self._playing_break: Optional[Break] = None

    @property
    def track_is_playing(self) -> bool:
        return self._currently_playing is not None

    @property
    def track_playing(self) -> Optional[ScheduledTrack]:
        return self._currently_playing

    @property
    def wait_until_track_playing_ends(self) -> Callable[[], Coroutine]:
        return self._track_playing_event.wait

    def update_no_track_playing(self) -> None:
        self._start_playing_dt = None
        self._playing_break = None
        self._currently_playing = None
        self._track_playing_event.set()

    def update_track_playing(self, track: ScheduledTrack, duration: Seconds) -> None:
        self._track_playing_event.clear()
        self._start_playing_dt = self._clock.now()
        self._playing_break = self._breaks.get_current()
        self._currently_playing = track

    def _emit_played_event(self, end_playing_dt: datetime) -> None:
        if (currently_playing := self._currently_playing) is None:
            raise RuntimeError("No currently playing!")
        if (playing_break := self._playing_break) is None:
            raise RuntimeError("No current playing break!")
        if (start_playing_dt := self._start_playing_dt) is None:
            raise RuntimeError("No playing start datetime!")

        track_played = TrackPlayed(
            identity=currently_playing.identity,
            break_=playing_break.ordinal,
            start=start_playing_dt,
            end=end_playing_dt,
            created=self._clock.now(),
        )
        playlist_producer.produce(track_played)

    def playing_ends_callback(self) -> None:
        # TODO
        # if player.playing:
        #     logger.error("How?!")
        #     player.stop()
        logger.debug("Playing ended")
        end_playing_dt = self._clock.now()
        self._emit_played_event(end_playing_dt)
        self.update_no_track_playing()
