from datetime import datetime, timedelta, timezone
from typing import Final
from kink import di
from pytest import fixture
from application.events.handle import EventHandler
from building_blocks.clock import FixedClock
from domain.breaks import Breaks
from domain.entities import (
    TrackProvidedIdentity,
    TrackToSchedule,
)
from domain.events.track import (
    PlayingTime,
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
)
from domain.repositories.scheduled_tracks import ScheduledTracksRepository
from domain.types import Identifier, Seconds
from ..bootstrap import reregister_deps_with_clock


dt: Final = datetime(2024, 8, 14, 14, 53, 16, tzinfo=timezone.utc)


@fixture
def repo() -> ScheduledTracksRepository:
    clock = FixedClock(dt)
    reregister_deps_with_clock(clock)
    repo = di[ScheduledTracksRepository]
    repo.delete_all()

    return repo


@fixture
def track_added(repo) -> TrackToSchedule:
    TRACK = TrackToSchedule(
        identity=TrackProvidedIdentity(
            identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
        ),
        break_=di[Breaks].as_list()[0],
        duration=Seconds(42),
    )
    repo.insert(TRACK)
    return TRACK


def test_adding_track_event_applied_twice_does_not_change_state(repo):
    event_handler = di[EventHandler]
    track_scheduled_datetime = dt + timedelta(days=1)
    identity = TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    event = TrackAddedToPlaylist(
        identity=identity,
        when=PlayingTime(break_=1, date_=track_scheduled_datetime.date()),
        duration=Seconds(42),
        waits_on_approval=False,
        created=dt - timedelta(seconds=3),
    )

    event_handler.handle_event(event)
    result_applied_once = repo.get_track_on(
        identity=identity, date_=track_scheduled_datetime.date(), break_=1
    )
    assert result_applied_once is not None

    event_handler.handle_event(event)
    result_applied_twice = repo.get_track_on(
        identity=identity, date_=track_scheduled_datetime.date(), break_=1
    )
    assert result_applied_once == result_applied_twice


def test_skips_event_adding_scheduled_track_if_waiting(repo):
    event_handler = di[EventHandler]
    identity = TrackProvidedIdentity(
        identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
    )
    when = PlayingTime(break_=1, date_=(dt + timedelta(days=1)).date())
    event = TrackAddedToPlaylist(
        identity=identity,
        when=when,
        duration=Seconds(42),
        waits_on_approval=True,
        created=dt - timedelta(seconds=3),
    )

    event_handler.handle_event(event)

    assert (
        repo.get_track_on(identity=identity, date_=when.date_, break_=when.break_)
        is None
    )


def test_deletes_scheduled_track(repo, track_added):
    event_handler = di[EventHandler]
    identity = track_added.identity
    when = PlayingTime(break_=track_added.break_.ordinal, date_=track_added.break_.date)
    event = TrackDeletedFromPlaylist(
        identity=identity,
        when=when,
        created=dt - timedelta(seconds=3),
    )
    got_track = repo.get_track_on(
        identity=identity, date_=when.date_, break_=when.break_
    )
    assert got_track is not None and got_track.identity == identity

    event_handler.handle_event(event)

    assert (
        repo.get_track_on(identity=identity, date_=when.date_, break_=when.break_)
        is None
    )
