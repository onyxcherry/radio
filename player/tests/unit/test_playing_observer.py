from datetime import date, datetime, time, timedelta
from typing import Final

from kink import di
from pytest import fixture
import pytest
from player.src.infrastructure.messaging.types import (
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)
from player.src.domain.repositories.scheduled_tracks import ScheduledTracksRepository
from player.src.application.playing_observer import PlayingObserver
from player.src.building_blocks.clock import FixedClock
from player.src.config import BreaksConfig
from player.src.domain.breaks import Breaks
from player.src.domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
)
from player.src.domain.types import Identifier, Seconds
from player.src.domain.events.track import TrackPlayed


breaks_config = di[BreaksConfig]

_day = date(2024, 8, 1)
dt = datetime.combine(_day, time(8, 34, 11), tzinfo=breaks_config.timezone)
clock = FixedClock(dt)
breaks = Breaks(config=breaks_config, clock=clock)

track_to_schedule: Final = TrackToSchedule(
    identity=TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    ),
    break_=breaks.as_list()[0],
    duration=Seconds(42),
)

scheduled_track: Final = ScheduledTrack(
    identity=TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    ),
    break_=breaks.as_list()[0],
    duration=Seconds(42),
    played=False,
    created=dt - timedelta(minutes=23),
    last_changed=dt - timedelta(minutes=23),
)

scheduled_tracks_repo = di[ScheduledTracksRepository]
events_consumer = di[PlaylistEventsConsumer]
events_producer = di[PlaylistEventsProducer]


@fixture(autouse=True)
def reset(reset_db_fixt, reset_events_fixt):
    scheduled_tracks_repo.insert(track_to_schedule)

    yield


@fixture
def pl_obs() -> PlayingObserver:
    playing_observer = PlayingObserver(breaks, scheduled_tracks_repo, clock=clock)
    return playing_observer


def test_updates_track_is_playing_then_stops(pl_obs):
    assert pl_obs.track_playing is None
    assert pl_obs.track_is_playing is False

    pl_obs.update_track_playing(scheduled_track, duration=Seconds(40))
    assert pl_obs.track_is_playing is True
    assert pl_obs.track_playing == scheduled_track

    pl_obs.update_no_track_playing()
    assert pl_obs.track_playing is None
    assert pl_obs.track_is_playing is False


@pytest.mark.asyncio
async def test_playing_ends_callback(pl_obs):
    pl_obs.update_track_playing(scheduled_track, duration=Seconds(40))

    pl_obs.playing_ends_callback()
    assert pl_obs.track_playing is None
    assert pl_obs.track_is_playing is False

    updated_track = scheduled_tracks_repo.get_track_on(
        scheduled_track.identity, dt.date()
    )
    assert updated_track is not None
    assert updated_track.played is True
    events = await events_consumer.consume(1)
    assert events[0] == TrackPlayed(
        identity=scheduled_track.identity,
        break_=0,
        start=datetime(2024, 8, 1, 8, 34, 11, tzinfo=breaks_config.timezone),
        end=datetime(2024, 8, 1, 8, 34, 11, tzinfo=breaks_config.timezone),
        created=datetime(2024, 8, 1, 8, 34, 11, tzinfo=breaks_config.timezone),
    )
