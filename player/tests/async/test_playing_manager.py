import asyncio
from datetime import datetime, timezone
from typing import Any, Final, Generator
from kink import di
import pytest

from player.src.application.break_observer import BreakObserver
from player.src.application.playing_observer import PlayingObserver
from player.src.building_blocks.clock import FeignedWallClock
from player.src.config import BreaksConfig
from player.src.domain.breaks import Breaks
from player.src.domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
)
from player.src.domain.events.track import TrackPlayed
from player.src.application.playing_manager import PlayingConditions, PlayingManager
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository
from player.src.domain.types import Identifier, Seconds
from player.src.infrastructure.messaging.types import PlaylistEventsConsumer
from player.tests.bootstrap import reregister_deps_with_clock

scheduled_track: Final = ScheduledTrack(
    identity=TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    ),
    break_=di[Breaks].as_list()[0],
    duration=Seconds(42),
    played=False,
    created=datetime(2024, 8, 1, 8, 34, 11, tzinfo=timezone.utc),
    last_changed=datetime(2024, 8, 1, 8, 34, 11, tzinfo=timezone.utc),
)

_tasks: list[asyncio.Task] = []


@pytest.fixture(autouse=True)
def reset(reset_db_fixt, reset_events_fixt):
    pass


def create_asyncio_task(task) -> None:
    task_run = asyncio.create_task(task)
    _tasks.append(task_run)


def get_playing_manager(at: datetime) -> PlayingManager:
    clock = FeignedWallClock(at)
    reregister_deps_with_clock(clock)
    playing_manager = di[PlayingManager]
    return playing_manager


@pytest.fixture
def pm_during_break(reset) -> Generator[PlayingManager, Any, Any]:
    timezone = di[BreaksConfig].timezone
    dt = datetime(2024, 8, 1, 8, 34, 11, tzinfo=timezone)
    yield get_playing_manager(dt)
    for task in _tasks:
        if task.done() or task.cancelled() or asyncio.get_event_loop().is_closed:
            continue
        task.cancel()


@pytest.fixture
def scheduled_track_ready():
    repo = di[ScheduledTracksRepository]
    track = TrackToSchedule(
        identity=TrackProvidedIdentity(
            identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
        ),
        break_=di[Breaks].as_list()[0],
        duration=Seconds(2),
    )
    repo.insert(track)


@pytest.fixture
def scheduled_track2_ready():
    repo = di[ScheduledTracksRepository]
    track = TrackToSchedule(
        identity=TrackProvidedIdentity(
            identifier=Identifier("y2zG-Rgz4rQ"), provider="Youtube"
        ),
        break_=di[Breaks].as_list()[0],
        duration=Seconds(3),
    )
    repo.insert(track)


@pytest.mark.skip()
@pytest.mark.asyncio
async def test_waits_when_manually_stopped(pm_during_break):
    playing_conditions = di[PlayingConditions]
    break_observer = di[BreakObserver]
    playing_manager = pm_during_break

    playing_conditions.manually_stopped.sleep_again()
    create_asyncio_task(playing_manager.until_music_should_play())
    create_asyncio_task(break_observer.update_current_break())

    await asyncio.sleep(0.1)
    assert playing_manager.waits

    await asyncio.sleep(0.1)

    playing_conditions.manually_stopped.awake()
    await asyncio.sleep(0.1)

    assert playing_manager.waits is False
    assert playing_manager.waits is True


@pytest.mark.asyncio
async def test_waits_for_playing_track_to_end(pm_during_break):
    playing_observer = di[PlayingObserver]
    break_observer = di[BreakObserver]
    playing_manager = pm_during_break

    playing_observer.update_track_playing(scheduled_track, Seconds(42))

    task = asyncio.create_task(playing_manager.until_music_should_play())
    auxiliary_task = asyncio.create_task(break_observer.update_current_break())

    await asyncio.sleep(0.01)
    assert playing_manager.waits
    await asyncio.sleep(0.01)

    playing_observer.update_no_track_playing()
    await asyncio.sleep(0.01)

    assert playing_manager.waits is False

    auxiliary_task.cancel()
    task.cancel()


@pytest.mark.asyncio
async def test_waits_to_next_break(): ...


@pytest.mark.asyncio
async def test_plays_track(pm_during_break, scheduled_track_ready):
    playing_observer = di[PlayingObserver]
    break_observer = di[BreakObserver]
    playing_manager = pm_during_break
    events_consumer = di[PlaylistEventsConsumer]

    create_asyncio_task(playing_manager.manage_playing())
    create_asyncio_task(break_observer.update_current_break())

    await asyncio.sleep(0.5)
    track_playing = playing_observer.track_playing
    assert track_playing is not None
    assert track_playing.identity == TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    assert track_playing.played is False

    await asyncio.sleep(2)

    repo = di[ScheduledTracksRepository]
    track = repo.get_track_on(
        track_playing.identity, date_=track_playing.break_.start.date()
    )
    assert track is not None and track.played is True
    assert playing_observer.track_is_playing is False
    consumed_events = await events_consumer.consume(1)
    event = consumed_events[0]
    assert isinstance(event, TrackPlayed)
    assert event.identity == TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    assert event.break_ == 1


@pytest.mark.asyncio
async def test_plays_next_track_after_ones_end(
    pm_during_break, scheduled_track_ready, scheduled_track2_ready
):
    playing_observer = di[PlayingObserver]
    break_observer = di[BreakObserver]
    playing_manager = pm_during_break

    create_asyncio_task(playing_manager.manage_playing())
    create_asyncio_task(break_observer.update_current_break())

    await asyncio.sleep(0.5)
    track_playing = playing_observer.track_playing
    assert track_playing is not None
    assert track_playing.identity == TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    assert track_playing.played is False

    await asyncio.sleep(2)

    track_playing = playing_observer.track_playing
    assert track_playing is not None
    assert track_playing.identity == TrackProvidedIdentity(
        identifier=Identifier("y2zG-Rgz4rQ"), provider="Youtube"
    )
    assert track_playing.played is False


def test_updates_status_to_no_playing_after_player_exception(
    pm_during_break, scheduled_track_ready
): ...
