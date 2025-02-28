import asyncio

from just_playback.ma_result import MiniaudioError
from kink import di, inject
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from application.break_observer import BreakObserver
from application.playing_observer import PlayingObserver
from application.track_file_provider import PlayableTrackProvider
from building_blocks.awakable import EventBasedAwakable
from config import get_logger
from domain.interfaces.player import Player

logger = get_logger(__name__)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PlayingConditions:
    manually_stopped: EventBasedAwakable
    stopped_due_to_tech_error: EventBasedAwakable


@inject
class PlayingManager:
    def __init__(
        self,
        playing_observer: PlayingObserver,
        break_observer: BreakObserver,
        playing_conditions: PlayingConditions,
        playable_track_provider: PlayableTrackProvider,
        player: Player,
    ) -> None:
        self._playing_observer = playing_observer
        self._break_observer = break_observer
        self._manually_stopped = playing_conditions.manually_stopped
        self._stopped_due_to_tech_error = playing_conditions.stopped_due_to_tech_error
        self._playable_track_provider = playable_track_provider
        self._player = player
        self._waits = True

    @property
    def waits(self) -> bool:
        return self._waits

    async def until_music_should_play(self) -> None:
        if self._manually_stopped.will_wait():
            self._waits = True
            await self._manually_stopped.wait_for()

        if self._playing_observer.track_is_playing:
            self._waits = True
            await self._playing_observer.wait_until_track_playing_ends()

        if self._break_observer.current is None:
            self._waits = True
            logger.debug("Waiting for next break")
            await self._break_observer.wait_next()

        self._waits = False

    def handle_playing_immediate_stop(self) -> None:
        self._player.stop(force=True)
        logger.warning("Immediately stopped playing")
        self._playing_observer.update_no_track_playing()

    async def manage_playing(self) -> None:
        logger.info("Started managing playing")
        while True:
            await self.until_music_should_play()

            track_to_play = self._playable_track_provider.get_track_to_play()
            logger.debug(f"{track_to_play=}")
            if track_to_play is None:
                self._playable_track_provider.add_track_to_play_miss()
                await self._playable_track_provider.wait_a_bit_on_track_to_play()
                continue

            self._player.load_file(track_to_play.path)

            track = track_to_play.track
            callback = self._playing_observer.playing_ends_callback
            playing_duration = min([track.duration, self._break_observer.seconds_left])
            self._playing_observer.update_track_playing(
                track, duration=playing_duration
            )
            try:
                await self._player.play(playing_duration, callback)
            except MiniaudioError as mex:
                self.handle_playing_immediate_stop()
                raise RuntimeError("Playing error :(") from mex
            # else:
            # TODO: fix this - execute in `else` block properly
            #     playing_observer.update_track_playing(track, duration=playing_duration)


async def main() -> None:
    playing_conditions = PlayingConditions(
        manually_stopped=EventBasedAwakable(),
        stopped_due_to_tech_error=EventBasedAwakable(),
    )
    playing_observer = di[PlayingObserver]
    break_observer = di[BreakObserver]
    playable_track_provider = di[PlayableTrackProvider]
    player = di[Player]
    playing_manager = PlayingManager(
        playing_observer,
        break_observer,
        playing_conditions,
        playable_track_provider,
        player,
    )
    await asyncio.gather(
        playing_manager.manage_playing(),
        break_observer.create_task(),
        # break_observer.update_current_break(),
        return_exceptions=True,
    )


# asyncio.run(main())
