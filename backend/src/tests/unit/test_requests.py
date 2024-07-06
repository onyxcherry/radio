from datetime import date
from typing import Any
from kink import di
from pytest import fixture, raises, mark
from track.builder import NotKnownProviderError
from building_blocks.clock import Clock
from tests.unit.data import FUTURE_PT, FUTURE_PT_WEEKEND, PASSED_PT, NEW_YT_TRACKS
from track.application.playlist import Playlist
from track.domain.entities import NewTrack, Status, TrackRequested
from track.application.library import Library
from track.application.requests_service import (
    MAX_TRACKS_QUEUED_ONE_BREAK,
    LibraryTrackError,
    PlayingTimeError,
    RequestsService,
)
from track.domain.breaks import Breaks, PlayingTime, get_breaks_durations
from track.domain.provided import Identifier, Seconds, TrackProvidedIdentity, TrackUrl

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
def yt_tracks():
    duration_sum = sum([(track.duration or 0) for track in NEW_YT_TRACKS])
    assert duration_sum < min(get_breaks_durations()) * 0.8

    for track in NEW_YT_TRACKS:
        library.add(track)


@fixture
def whole_break_scheduled():
    playing_time = FUTURE_PT

    break_duration = get_breaks_durations()[
        playing_time.break_.get_number_from_zero_of()
    ]
    tracks_count = 4
    for idx in range(1, tracks_count + 1):
        identifier = f"{idx}".rjust(11, "a")
        track = NewTrack(
            TrackProvidedIdentity(
                identifier=Identifier(identifier), provider="Youtube"
            ),
            title=f"Track {idx}",
            url=TrackUrl(f"https://www.youtube.com/watch?v={identifier}"),
            duration=Seconds(break_duration // tracks_count),
        )
        library.add(track)
        library.accept(track.identity)

        req = TrackRequested(track.identity, playing_time)
        playlist.add(req)


@fixture
def max_tracks_count_on_queue():
    playing_time = FUTURE_PT

    for idx in range(1, MAX_TRACKS_QUEUED_ONE_BREAK + 1):
        identifier = f"{idx}".rjust(11, "a")
        track = NewTrack(
            TrackProvidedIdentity(
                identifier=Identifier(identifier), provider="Youtube"
            ),
            title=f"Track {idx}",
            url=TrackUrl(f"https://www.youtube.com/watch?v={identifier}"),
            duration=Seconds(3 * idx),
        )
        library.add(track)
        library.accept(track.identity)

        req = TrackRequested(track.identity, playing_time)
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
    assert errors is None

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
    assert errors is not None and len(errors) == 1
    assert errors[0] == LibraryTrackError.INVALID_DURATION


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
    assert errors is None

    got_track = library.get(identity)
    assert got_track is not None
    assert got_track.identity == identity
    assert got_track.status == Status.PENDING_APPROVAL

@mark.realdb()
def test_adds_new_track_to_playlist():
    track = NEW_YT_TRACKS[0]
    pt = FUTURE_PT

    result = rs.request_on(track.identity, pt)

    assert result.success is True
    assert result.errors is None
    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is not None
    assert got_track.when == pt

@mark.realdb()
def test_adds_pending_approval_track_to_playlist(yt_tracks):
    track = NEW_YT_TRACKS[0]
    pt = FUTURE_PT

    result = rs.request_on(track.identity, pt)

    assert result.success is True
    assert result.errors is None
    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is not None
    assert got_track.when == pt

@mark.realdb()
def test_adds_accepted_track_to_playlist(yt_tracks):
    track = NEW_YT_TRACKS[0]
    library.accept(track.identity)
    pt = FUTURE_PT

    result = rs.request_on(track.identity, pt)

    assert result.success is True
    assert result.errors is None
    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is not None
    assert got_track.when == pt


def test_not_add_rejected_track_to_playlist(yt_tracks):
    track = NEW_YT_TRACKS[0]
    library.reject(track.identity)
    pt = FUTURE_PT

    result = rs.request_on(track.identity, pt)

    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == LibraryTrackError.TRACK_REJECTED

    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is None

@mark.realdb()
def test_error_as_requested_pt_passed(yt_tracks):
    track = NEW_YT_TRACKS[0]
    result = rs.request_on(track.identity, PASSED_PT)
    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == PlayingTimeError.IN_THE_PAST

@mark.realdb()
def test_error_as_requested_on_weekend(yt_tracks):
    track = NEW_YT_TRACKS[0]

    result = rs.request_on(track.identity, FUTURE_PT_WEEKEND)
    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == PlayingTimeError.AT_THE_WEEKEND

@mark.realdb()
def test_error_as_track_played_on_this_day(yt_tracks):
    track = NEW_YT_TRACKS[0]
    library.accept(track.identity)
    same_day = date(2099, 1, 1)
    pt1 = PlayingTime(break_=Breaks.FIRST, date_=same_day)
    pt2 = PlayingTime(break_=Breaks.SECOND, date_=same_day)

    assert rs.request_on(track.identity, pt1).success is True
    queued = playlist.get(track.identity, pt1.date_)
    assert queued is not None
    playlist.mark_as_played(queued)

    result = rs.request_on(track.identity, pt2)

    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == PlayingTimeError.ALREADY_ON_THIS_DAY

@mark.realdb()
def test_error_as_track_already_queued_on_this_day(yt_tracks):
    track = NEW_YT_TRACKS[0]
    library.accept(track.identity)
    same_day = date(2099, 1, 1)
    pt1 = PlayingTime(break_=Breaks.FIRST, date_=same_day)
    pt2 = PlayingTime(break_=Breaks.SECOND, date_=same_day)
    assert rs.request_on(track.identity, pt1).success is True

    result = rs.request_on(track.identity, pt2)

    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == PlayingTimeError.ALREADY_ON_THIS_DAY

@mark.realdb()
def test_error_as_no_left_time_on_break(yt_tracks, whole_break_scheduled):
    track = NEW_YT_TRACKS[0]
    result = rs.request_on(track.identity, FUTURE_PT)

    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == PlayingTimeError.NOT_ENOUGH_TIME

@mark.realdb()
def test_error_as_max_queue_count_exceeded(yt_tracks, max_tracks_count_on_queue):
    track = NEW_YT_TRACKS[0]
    result = rs.request_on(track.identity, FUTURE_PT)

    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 1
    assert result.errors[0] == PlayingTimeError.MAX_COUNT_EXEEDED

@mark.realdb()
def test_multiple_playlist_errors(yt_tracks, whole_break_scheduled):
    scheduled_track = playlist.get_all(FUTURE_PT.date_)[0]
    result = rs.request_on(scheduled_track.identity, scheduled_track.when)

    expected_errors_set = set(
        [PlayingTimeError.NOT_ENOUGH_TIME, PlayingTimeError.ALREADY_ON_THIS_DAY]
    )
    assert result.success is False
    assert result.errors is not None
    assert len(result.errors) == 2
    assert set(result.errors) == expected_errors_set


# def test_waiting_track_doesnt_count_into_number_of_tracks_limit():
#     playing_time = FUTURE_PT

#     for track in PENDING_APPROVAL_TRACKS:
#         library_repo.add(track)
#         assert rs.request_on(track.identity, playing_time).success is True

#     # def test_waiting_track_doesnt_count_into_duration_sum_limit(yt_tracks):


# #     playlist.add()
#     count = playlist.get_tracks_duration_on_break()
#     playlist.
#     assert count == 1
