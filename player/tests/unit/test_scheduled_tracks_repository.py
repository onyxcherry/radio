from datetime import datetime, timedelta, timezone
from typing import Final

from kink import di
from pytest import fixture

from building_blocks.clock import FixedClock
from domain.breaks import Breaks
from domain.entities import (
    ScheduledTrack,
    TrackProvidedIdentity,
    TrackToSchedule,
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
def tracks_added(repo) -> list[TrackToSchedule]:
    TRACK: Final = TrackToSchedule(
        identity=TrackProvidedIdentity(
            identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
        ),
        break_=di[Breaks].as_list()[0],
        duration=Seconds(42),
    )
    ANOTHER_TRACK: Final = TrackToSchedule(
        identity=TrackProvidedIdentity(
            identifier=Identifier("y2zG-Rgz4rQ"), provider="Youtube"
        ),
        break_=di[Breaks].as_list()[0],
        duration=Seconds(23),
    )
    repo.insert(TRACK)
    repo.insert(ANOTHER_TRACK)
    return [TRACK, ANOTHER_TRACK]


def test_gets_track(repo, tracks_added):
    TRACK = tracks_added[0]
    identity = TRACK.identity
    date_ = TRACK.break_.date
    break_ = TRACK.break_.ordinal
    result = repo.get_track_on(identity, date_, break_)

    assert result is not None
    assert result.identity == identity
    assert result.break_.date == date_
    assert result.break_.ordinal == break_


def test_gets_all_tracks(repo, tracks_added):
    TRACK = tracks_added[0]
    date_ = TRACK.break_.date
    break_ = TRACK.break_.ordinal
    result = repo.get_all(date_, break_)

    assert result is not None and len(result) == 2
    assert result[0].identity == TRACK.identity
    assert result[0].break_.date == date_
    assert result[0].break_.ordinal == break_


def test_inserts_track(repo):
    TRACK = TrackToSchedule(
        identity=TrackProvidedIdentity(
            identifier=Identifier("cTAYaZkOvV8"), provider="Youtube"
        ),
        break_=di[Breaks].as_list()[0],
        duration=Seconds(42),
    )
    repo.insert(TRACK)

    result = repo.get_track_on(TRACK.identity, TRACK.break_.date, TRACK.break_.ordinal)
    expected = ScheduledTrack(
        identity=TRACK.identity,
        break_=TRACK.break_,
        duration=TRACK.duration,
        played=False,
        created=dt,
        last_changed=dt,
    )
    assert result == expected


def test_updates_track(repo, tracks_added):
    TRACK = tracks_added[0]
    result = repo.get_track_on(TRACK.identity, TRACK.break_.date, TRACK.break_.ordinal)
    assert result is not None

    modified_track = ScheduledTrack(
        identity=result.identity,
        break_=result.break_,
        duration=result.duration,
        played=True,
        created=dt,
        last_changed=dt,
    )
    assert repo.update(modified_track) == modified_track
    assert (
        repo.get_track_on(TRACK.identity, TRACK.break_.date, TRACK.break_.ordinal)
        == modified_track
    )


def test_does_not_update_last_changed_if_no_other_field_is_changing(repo, tracks_added):
    TRACK = tracks_added[0]
    got_track = repo.get_track_on(
        TRACK.identity, TRACK.break_.date, TRACK.break_.ordinal
    )
    assert got_track is not None

    example_dt = dt + timedelta(minutes=3, seconds=12)
    modified_track = ScheduledTrack(
        identity=got_track.identity,
        break_=got_track.break_,
        duration=got_track.duration,
        played=got_track.played,
        created=got_track.created,
        last_changed=example_dt,
    )
    update_result = repo.update(modified_track)
    assert update_result != modified_track
    assert update_result.last_changed != modified_track.last_changed
    assert update_result.last_changed == got_track.last_changed


def test_deletes_track(repo, tracks_added):
    TRACK = tracks_added[0]
    got_track = repo.get_track_on(
        TRACK.identity, TRACK.break_.date, TRACK.break_.ordinal
    )
    assert got_track is not None

    assert repo.delete(got_track) == got_track
    assert (
        repo.get_track_on(TRACK.identity, TRACK.break_.date, TRACK.break_.ordinal)
        is None
    )
    assert len(repo.get_all(TRACK.break_.date)) == 1


def test_deletes_all_tracks_from_queue(repo, tracks_added):
    TRACK = tracks_added[0]
    result = repo.delete_all()
    assert result == 2
    assert len(repo.get_all(TRACK.break_.date)) == 0


def test_deletes_all_tracks_with_identity(repo, tracks_added):
    TRACK = tracks_added[0]
    result = repo.delete_all_with_identity(TRACK.identity)
    assert result == 1
    assert len(repo.get_all(TRACK.break_.date)) == 1
