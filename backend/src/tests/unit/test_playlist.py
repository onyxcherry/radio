from datetime import datetime
from kink import di
from pytest import fixture, mark
from tests.conftest import sync_messages_from_producer_to_consumer
from track.domain.events.playlist import (
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
    TrackMarkedAsPlayed,
)
from building_blocks.clock import Clock
from track.application.interfaces.events import EventsConsumer
from track.application.library import Library
from track.domain.entities import TrackRequested
from track.application.playlist import Playlist
from .data import ACCEPTED_TRACKS, FUTURE_PT, PENDING_APPROVAL_TRACKS

playlist = di[Playlist]
library = di[Library]
events_consumer = di[EventsConsumer]
events_consumer.subscribe([library._events_topic, playlist._events_topic])
events_producer = library._events_producer
clock = di[Clock]

fixed_dt = datetime(2024, 7, 16, 14, 19, 21)


def sync_messages():
    sync_messages_from_producer_to_consumer(events_producer, events_consumer)


@fixture(autouse=True)
def reset():
    playlist_repo = playlist._playlist_repository
    library_repo = library._library_repository
    playlist_repo.delete_all()
    library_repo.delete_all()

    yield

    playlist_repo.delete_all()
    library_repo.delete_all()


@fixture
def accepted_tracks():
    library_repo = library._library_repository

    for track in ACCEPTED_TRACKS:
        library_repo.add(track)


@fixture
def pending_approval_tracks():
    library_repo = library._library_repository

    for track in PENDING_APPROVAL_TRACKS:
        library_repo.add(track)


@mark.realdb()
def test_adds_track_to_playlist(accepted_tracks):
    playing_time = FUTURE_PT
    requested = TrackRequested(ACCEPTED_TRACKS[0].identity, playing_time)

    playlist.add(requested)

    playlist_tracks_list = playlist.get_all(playing_time.date_)

    track_queued = playlist_tracks_list[0]
    assert track_queued.identity == requested.identity
    assert track_queued.when == playing_time
    sync_messages()
    expected_event = TrackAddedToPlaylist(
        identity=requested.identity,
        when=requested.when,
        waits_on_approval=False,
        created=fixed_dt,
    )
    assert expected_event in events_consumer.consume(10)


def test_deletes_track(accepted_tracks):
    playing_time = FUTURE_PT
    identity = ACCEPTED_TRACKS[0].identity
    requested = TrackRequested(identity, playing_time)

    added = playlist.add(requested)

    playlist.delete(added)

    assert playlist.get(identity, playing_time.date_) is None
    sync_messages()
    expected_event = TrackDeletedFromPlaylist(
        identity=identity, when=playing_time, created=fixed_dt
    )
    assert expected_event in events_consumer.consume(10)


def test_marks_as_played(accepted_tracks):
    requested = TrackRequested(ACCEPTED_TRACKS[0].identity, FUTURE_PT)
    playlist.add(requested)

    track = playlist.get(
        requested.identity, requested.when.date_, requested.when.break_
    )
    assert track is not None
    assert track.played is False

    playlist.mark_as_played(track)

    track_marked = playlist.get(
        requested.identity, requested.when.date_, requested.when.break_
    )
    assert track_marked is not None
    assert track_marked.played is True
    sync_messages()
    expected_event = TrackMarkedAsPlayed(
        identity=requested.identity, when=requested.when, created=fixed_dt
    )
    assert expected_event in events_consumer.consume(10)


@mark.realdb()
def test_gets_tracks_count(accepted_tracks, pending_approval_tracks):
    playing_time = FUTURE_PT
    playlist.add(TrackRequested(PENDING_APPROVAL_TRACKS[0].identity, playing_time))
    playlist.add(TrackRequested(PENDING_APPROVAL_TRACKS[1].identity, playing_time))
    playlist.add(TrackRequested(ACCEPTED_TRACKS[0].identity, playing_time))

    assert playlist.get_tracks_count_on_break(playing_time, waiting=True) == 2
    assert playlist.get_tracks_count_on_break(playing_time, waiting=False) == 1
    assert playlist.get_tracks_count_on_break(playing_time) == 3


@mark.realdb()
def test_gets_tracks_duration(accepted_tracks, pending_approval_tracks):
    playing_time = FUTURE_PT
    track1 = PENDING_APPROVAL_TRACKS[0]
    track2 = PENDING_APPROVAL_TRACKS[1]
    track3 = ACCEPTED_TRACKS[0]

    playlist.add(TrackRequested(track1.identity, playing_time))
    playlist.add(TrackRequested(track2.identity, playing_time))
    playlist.add(TrackRequested(track3.identity, playing_time))

    sum_1_2 = sum([track1.duration or 0, track2.duration or 0])
    dur_3 = track3.duration or 0

    assert playlist.get_tracks_duration_on_break(playing_time, waiting=True) == sum_1_2
    assert playlist.get_tracks_duration_on_break(playing_time, waiting=False) == dur_3
    assert playlist.get_tracks_duration_on_break(playing_time) == sum_1_2 + dur_3


def test_checks_track_played_or_queued_this_day(accepted_tracks):
    identity = ACCEPTED_TRACKS[0].identity
    playing_time = FUTURE_PT
    requested = TrackRequested(identity, playing_time)

    queued = playlist.add(requested)

    assert playlist.check_played_or_queued_on_day(identity, playing_time.date_) is True

    playlist.mark_as_played(queued)

    assert playlist.check_played_or_queued_on_day(identity, playing_time.date_) is True
