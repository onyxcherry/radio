from datetime import date
from typing import Any
from kink import di
from pytest import fixture, raises, mark
from track.builder import NotKnownProviderError
from building_blocks.clock import Clock
from tests.unit.data import (
    FUTURE_PT,
    FUTURE_PT_WEEKEND,
    NEW_TRACKS,
    PASSED_PT,
    TRACKS,
    NEW_YT_TRACKS,
)
from track.domain.errors import PlayingTimeError, TrackDurationExceeded
from track.application.playlist import Playlist
from track.domain.entities import NewTrack, Status, TrackRequested
from track.application.library import Library
from track.application.requests_service import RequestsService
from track.domain.breaks import Breaks, PlayingTime
from track.domain.provided import (
    Identifier,
    ProviderName,
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)

system_clock = di[Clock]
playlist = di[Playlist]
library = di[Library]
playlist_repo = playlist._playlist_repository
library_repo = library._library_repository

rs = RequestsService(
    library_repo,
    playlist_repo,
    system_clock,
)


@fixture
def tracks():
    for track in NEW_TRACKS:
        library.add(track)


@fixture
def yt_tracks():
    for track in NEW_YT_TRACKS:
        library.add(track)


@fixture
def whole_break_scheduled():
    for track in TRACKS:
        req = TrackRequested(track.identity, FUTURE_PT)
        playlist.add(req)


@fixture(autouse=True)
def reset():
    playlist_repo.delete_all()
    library_repo.delete_all()

    yield

    playlist_repo.delete_all()
    library_repo.delete_all()


def test_adds_track_to_library_successfully():
    identity = NEW_YT_TRACKS[0].identity
    result, errors = rs.add_to_library(identity)
    assert result.added is True
    assert result.waits_on_decision is True
    assert len(errors) == 0

    got_track = library.get(identity)
    assert got_track is not None
    assert got_track.identity == identity


def test_too_long_track_not_added_to_library():
    identity = TrackProvidedIdentity(
        identifier=Identifier("c_iRx2Un07k"), provider="Youtube"
    )
    result, errors = rs.add_to_library(identity)
    assert result.added is False
    assert result.waits_on_decision is False
    assert len(errors) == 1
    assert isinstance(errors[0], TrackDurationExceeded)


def test_no_provider_matched_for_track_requested():
    notknownprovider: Any = "notknownprovider"
    identity = TrackProvidedIdentity(
        identifier=Identifier("sth"), provider=notknownprovider
    )
    with raises(NotKnownProviderError):
        rs.add_to_library(identity)


def test_requests_to_add_already_pending_approval_track_in_library():
    identity = TrackProvidedIdentity(identifier=Identifier("a123"), provider="file")
    track = NewTrack(
        identity,
        title="A - B",
        url=TrackUrl("https://wisniewski.app/v=a123"),
        duration=Seconds(42),
    )
    library.add(track)

    result, errors = rs.add_to_library(identity)

    assert result.added is False
    assert result.waits_on_decision is True
    assert len(errors) == 0

    got_track = library.get(identity)
    assert got_track is not None
    assert got_track.identity == identity
    assert got_track.status == Status.PENDING_APPROVAL


def test_adds_track_to_playlist(yt_tracks):
    track = NEW_YT_TRACKS[0]
    pt = FUTURE_PT

    result = rs.request_on(track.identity, pt)

    assert result.success is True
    assert result.errors is None
    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is not None
    assert got_track.when == pt


def test_error_as_requested_pt_passed(yt_tracks):
    track = NEW_YT_TRACKS[0]
    result = rs.request_on(track.identity, PASSED_PT)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(result.errors[0], PlayingTimeError)


def test_error_as_requested_on_weekend(yt_tracks):
    track = NEW_YT_TRACKS[0]

    result = rs.request_on(track.identity, FUTURE_PT_WEEKEND)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(result.errors[0], PlayingTimeError)


def test_error_as_track_played_on_this_day(yt_tracks):
    track = NEW_YT_TRACKS[0]
    same_day = date(2099, 1, 1)
    pt1 = PlayingTime(
        break_=Breaks.FIRST,
        date_=same_day,
    )
    pt2 = PlayingTime(
        break_=Breaks.SECOND,
        date_=same_day,
    )
    assert rs.request_on(track.identity, pt1).success is True
    queued = playlist.get_all(pt1.date_)[0]
    playlist.mark_as_played(queued)

    result = rs.request_on(track.identity, pt2)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(result.errors[0], PlayingTimeError)


def test_error_as_track_already_queued_on_this_day(yt_tracks):
    track = NEW_YT_TRACKS[0]
    same_day = date(2099, 1, 1)
    pt1 = PlayingTime(
        break_=Breaks.FIRST,
        date_=same_day,
    )
    pt2 = PlayingTime(
        break_=Breaks.SECOND,
        date_=same_day,
    )
    assert rs.request_on(track.identity, pt1).success is True

    result = rs.request_on(track.identity, pt2)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(result.errors[0], PlayingTimeError)


@mark.skip()
def test_error_as_no_left_time_on_break(tracks, whole_break_scheduled):
    not_scheduled_track = NEW_YT_TRACKS[0]
    result = rs.request_on(not_scheduled_track.identity, FUTURE_PT)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(result.errors[0], PlayingTimeError)


def test_error_as_max_queue_count_exceeded(tracks):
    pass


@mark.skip()
def test_multiple_playlist_errors(tracks, whole_break_scheduled):
    scheduled_track = TRACKS[0]
    result = rs.request_on(scheduled_track.identity, FUTURE_PT)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(result.errors[0], PlayingTimeError)
    assert isinstance(result.errors[1], PlayingTimeError)
