from datetime import date
from typing import Any

from kink import di
from pydantic import ValidationError
from pytest import fixture, mark, raises

from building_blocks.clock import Clock
from config import Config
from tests.helpers.dt import fixed_dt
from tests.unit.data import FUTURE_PT, FUTURE_PT_WEEKEND, NEW_YT_TRACKS, PASSED_PT
from track.application.interfaces.events import EventsConsumer, EventsProducer
from track.application.library import Library
from track.application.playlist import Playlist
from track.application.requests_service import (
    LibraryTrackError,
    PlayingTimeError,
    RequestsService,
)
from track.domain.breaks import Breaks, PlayingTime
from track.domain.entities import NewTrack, Status, TrackRequested
from track.domain.events.library import TrackAccepted, TrackRejected
from track.domain.events.playlist import TrackDeletedFromPlaylist
from track.domain.provided import Identifier, Seconds, TrackProvidedIdentity, TrackUrl
from track.infrastructure.messaging.types import (
    LibraryEventsConsumer,
    LibraryEventsProducer,
    PlaylistEventsConsumer,
    PlaylistEventsProducer,
)

clock = di[Clock]
config = di[Config]
library_events_producer: EventsProducer = di[LibraryEventsProducer]
library_events_consumer: EventsConsumer = di[LibraryEventsConsumer]
playlist_events_producer: EventsProducer = di[PlaylistEventsProducer]
playlist_events_consumer: EventsConsumer = di[PlaylistEventsConsumer]
playlist = di[Playlist]
library = di[Library]
playlist_repo = playlist._playlist_repository
library_repo = library._library_repository

rs = RequestsService(
    library_repo,
    playlist_repo,
    library_events_producer,
    playlist_events_producer,
    playlist_events_consumer,
    config,
    clock,
)


@fixture(autouse=True)
def reset():
    playlist_repo.delete_all()
    library_repo.delete_all()

    yield

    playlist_repo.delete_all()
    library_repo.delete_all()


@fixture
def yt_tracks():
    for track in NEW_YT_TRACKS:
        library.add(track)


@fixture
def whole_break_scheduled():
    playing_time = FUTURE_PT

    break_duration = config.breaks.breaks[
        playing_time.break_.get_number_from_zero_of()
    ].duration
    assert break_duration is not None
    tracks_count = 4
    for idx in range(1, tracks_count + 1):
        identifier = f"{idx}".rjust(11, "a")
        duration = Seconds(break_duration // tracks_count)
        track = NewTrack(
            TrackProvidedIdentity(
                identifier=Identifier(identifier), provider="Youtube"
            ),
            title=f"Track {idx}",
            url=TrackUrl(f"https://www.youtube.com/watch?v={identifier}"),
            duration=duration,
        )
        library.add(track)
        rs.accept(track.identity)

        req = TrackRequested(track.identity, playing_time, duration)
        playlist.add(req)


@fixture
def max_tracks_count_on_queue():
    playing_time = FUTURE_PT
    for idx in range(1, config.tracks.queued_one_break_max + 1):
        identifier = f"{idx}".rjust(11, "a")
        duration = Seconds(3 * idx)
        track = NewTrack(
            TrackProvidedIdentity(
                identifier=Identifier(identifier), provider="Youtube"
            ),
            title=f"Track {idx}",
            url=TrackUrl(f"https://www.youtube.com/watch?v={identifier}"),
            duration=duration,
        )
        library.add(track)
        rs.accept(track.identity)

        req = TrackRequested(track.identity, playing_time, Seconds(3 * idx))
        playlist.add(req)


def test_adds_track_to_library_successfully():
    identity = NEW_YT_TRACKS[0].identity
    result = rs.add_to_library(identity)
    assert result.added is True
    assert result.waits_on_decision is True
    assert result.errors is None

    got_track = library.get(identity)
    assert got_track is not None
    assert got_track.identity == identity


def test_too_long_track_not_added_to_library():
    identity = TrackProvidedIdentity(
        identifier=Identifier("c_iRx2Un07k"), provider="Youtube"
    )
    result = rs.add_to_library(identity)
    errors = result.errors
    assert result.added is False
    assert result.waits_on_decision is False
    assert errors is not None and len(errors) == 1
    assert errors[0] == LibraryTrackError.INVALID_DURATION


def test_no_provider_matched_for_track_requested():
    notknownprovider: Any = "notknownprovider"
    with raises(ValidationError):
        _ = TrackProvidedIdentity(
            identifier=Identifier("sth"), provider=notknownprovider
        )


def test_requests_to_add_already_pending_approval_track_in_library():
    identity = TrackProvidedIdentity(identifier=Identifier("a123"), provider="file")
    track = NewTrack(
        identity,
        title="A - B",
        url=TrackUrl("https://wisniewski.app/v=a123"),
        duration=Seconds(42),
    )
    library.add(track)

    result = rs.add_to_library(identity)

    assert result.added is False
    assert result.waits_on_decision is True
    assert result.errors is None

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
    rs.accept(track.identity)
    pt = FUTURE_PT

    result = rs.request_on(track.identity, pt)

    assert result.success is True
    assert result.errors is None
    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is not None
    assert got_track.when == pt


def test_not_add_rejected_track_to_playlist(yt_tracks):
    track = NEW_YT_TRACKS[0]
    rs.reject(track.identity)
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
    rs.accept(track.identity)
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
    rs.accept(track.identity)
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


@mark.realdb()
def test_accept_track(yt_tracks, reset_events_fixt):
    track = NEW_YT_TRACKS[0]

    rs.accept(track.identity)

    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.ACCEPTED
    expected_event = TrackAccepted(
        identity=track.identity,
        previous_status=Status.PENDING_APPROVAL,
        created=fixed_dt,
    )
    assert expected_event in library_events_consumer.consume(1)


def test_reject_track(yt_tracks, reset_events_fixt):
    track = NEW_YT_TRACKS[0]

    rs.reject(track.identity)

    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.REJECTED
    expected_event = TrackRejected(
        identity=track.identity,
        previous_status=Status.PENDING_APPROVAL,
        created=fixed_dt,
    )
    assert expected_event in library_events_consumer.consume(1)


@mark.realdb()
def test_rejecting_track_removes_all_playlist_occurrences(yt_tracks, reset_events_fixt):
    track = NEW_YT_TRACKS[0]
    rs.accept(track.identity)
    first_pt = PlayingTime(break_=Breaks.FIRST, date_=date(2099, 4, 1))
    second_pt = PlayingTime(break_=Breaks.FIRST, date_=date(2099, 4, 2))
    assert playlist.add(TrackRequested(track.identity, first_pt, Seconds(23)))
    assert playlist.add(TrackRequested(track.identity, second_pt, Seconds(23)))

    rs.reject(track.identity)

    assert playlist.get(track.identity, first_pt.date_) is None
    assert playlist.get(track.identity, second_pt.date_) is None

    event_1 = TrackDeletedFromPlaylist(
        identity=track.identity, when=first_pt, created=fixed_dt
    )
    event_2 = TrackDeletedFromPlaylist(
        identity=track.identity, when=second_pt, created=fixed_dt
    )
    events = playlist_events_consumer.consume(4)
    assert event_1 in events
    assert event_2 in events
