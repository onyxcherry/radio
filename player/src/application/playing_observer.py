import asyncio
from datetime import datetime
from typing import Callable, Coroutine, Optional

from kink import di

from building_blocks.clock import Clock
from config import get_logger
from domain.breaks import Break, Breaks
from domain.entities import ScheduledTrack
from domain.events.track import TrackPlayed
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Seconds
from infrastructure.messaging.types import PlaylistEventsProducer

logger = get_logger(__name__)


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
        playlist_producer = di[PlaylistEventsProducer]
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

    def _mark_as_played(self, end_playing_dt: datetime) -> None:
        if (currently_playing := self._currently_playing) is None:
            raise RuntimeError("No currently playing!")
        marked = ScheduledTrack(
            identity=currently_playing.identity,
            break_=currently_playing.break_,
            duration=currently_playing.duration,
            played=True,
            created=currently_playing.created,
            last_changed=currently_playing.last_changed,
        )
        self._scheduled_tracks_repo.update(marked)

    def playing_ends_callback(self) -> None:
        # TODO
        # if player.playing:
        #     logger.error("How?!")
        #     player.stop()
        logger.debug("Playing ended")
        end_playing_dt = self._clock.now()
        self._mark_as_played(end_playing_dt)
        self._emit_played_event(end_playing_dt)
        self.update_no_track_playing()
