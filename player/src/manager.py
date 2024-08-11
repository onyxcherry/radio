import asyncio
from pathlib import Path

from kink import di
from player.src.application.break_observer import BreakObserver
from player.src.application.player_status import PlayerStatus
from player.src.application.playing_observer import PlayingObserver
from player.src.application.track_file_provider import (
    PlayableTrackProvider,
    PlayableTrackProviderConfig,
)
from player.src.building_blocks.awakable import EventBasedAwakable
from player.src.config import get_logger
from player.src.domain.breaks import Breaks
from player.src.building_blocks.clock import Clock
from player.src.domain.interfaces.player import Player
from player.src.domain.events.track import Event
from just_playback.ma_result import MiniaudioError

from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository

logger = get_logger(__name__)

_clock = di[Clock]
breaks = di[Breaks]
player = di[Player]
scheduled_tracks_repo = di[ScheduledTracksRepository]


break_observer = BreakObserver(breaks=breaks, clock=_clock)
playing_observer = PlayingObserver(
    breaks=breaks, scheduled_tracks_repo=scheduled_tracks_repo, clock=_clock
)
player_status = PlayerStatus(playing_observer, break_observer)
test_data_dir = Path("/home/tomasz/radio/player/tests/data/")
playable_track_provider = PlayableTrackProvider(
    config=PlayableTrackProviderConfig(test_data_dir)
)


class EventSendingQueue:
    def __init__(self) -> None:
        pass

    def add(self, event: Event) -> None:
        logger.info(event)


event_sending_queue = EventSendingQueue()


manually_stopped = EventBasedAwakable()


async def until_music_should_play() -> None:
    if manually_stopped.will_wait():
        await manually_stopped.wait_for()

    if playing_observer.track_is_playing:
        await playing_observer.wait_until_track_playing_ends()

    if not player_status.during_break:
        logger.debug("Waiting for next break")
        await break_observer.wait_next()


async def manage_playing() -> None:
    while True:
        await until_music_should_play()

        track_to_play = playable_track_provider.get_track_to_play()
        if track_to_play is None:
            playable_track_provider.add_track_to_play_miss()
            await playable_track_provider.wait_a_bit_on_track_to_play()
            continue

        player.load_file(track_to_play.path)

        track = track_to_play.track
        callback = playing_observer.playing_ends_callback
        playing_duration = min([track.duration, break_observer.seconds_left])
        playing_observer.update_track_playing(track, duration=playing_duration)
        try:
            player.play(playing_duration, callback)
        except MiniaudioError as mex:
            playing_observer.update_no_track_playing()
            raise RuntimeError("Playing error :(") from mex
        # else:
        # TODO: fix this - execute in `else` block properly
        #     playing_observer.update_track_playing(track, duration=playing_duration)


async def main() -> None:
    await asyncio.gather(
        manage_playing(),
        break_observer.create_task(),
        # break_observer.update_current_break(),
        return_exceptions=True,
    )


asyncio.run(main())
