from kink import di
from pytest import fixture, mark

from building_blocks.clock import Clock
from tests.helpers.dt import fixed_dt
from track.application.library import Library
from track.application.playlist import Playlist
from track.domain.entities import TrackRequested
from track.domain.events.playlist import (
    TrackAddedToPlaylist,
    TrackDeletedFromPlaylist,
    TrackMarkedAsPlayed,
)
from track.domain.provided import Seconds
from track.infrastructure.messaging.types import PlaylistEventsConsumer

from .data import ACCEPTED_TRACKS, FUTURE_PT, PENDING_APPROVAL_TRACKS

playlist = di[Playlist]
library = di[Library]
playlist_repo = playlist._playlist_repository
library_repo = library._library_repository
events_consumer = di[PlaylistEventsConsumer]
events_consumer.subscribe(playlist._events_topic)
events_producer = playlist._events_producer
clock = di[Clock]


@fixture(autouse=True)
def reset():
    playlist_repo.delete_all()
    library_repo.delete_all()

    yield

    playlist_repo.delete_all()
    library_repo.delete_all()


@fixture
def accepted_tracks(reset):
    for track in ACCEPTED_TRACKS:
        library_repo.add(track)


@fixture
def pending_approval_tracks(reset):
    for track in PENDING_APPROVAL_TRACKS:
        library_repo.add(track)


@mark.realdb()
def test_adds_track_to_playlist(accepted_tracks, reset_events_fixt):
    playing_time = FUTURE_PT
    requested = TrackRequested(ACCEPTED_TRACKS[0].identity, playing_time, Seconds(189))

    playlist.add(requested)

    playlist_tracks_list = playlist.get_all(playing_time.date_)

    track_queued = playlist_tracks_list[0]
    assert track_queued.identity == requested.identity
    assert track_queued.when == playing_time
    expected_event = TrackAddedToPlaylist(
        identity=requested.identity,
        when=requested.when,
        duration=Seconds(189),
        waits_on_approval=False,
        created=fixed_dt,
    )
    assert expected_event in events_consumer.consume(1)


def test_deletes_track(accepted_tracks, reset_events_fixt):
    playing_time = FUTURE_PT
    identity = ACCEPTED_TRACKS[0].identity
    requested = TrackRequested(identity, playing_time, Seconds(42))

    added = playlist.add(requested)

    playlist.delete(added)

    assert playlist.get(identity, playing_time.date_) is None
    expected_event = TrackDeletedFromPlaylist(
        identity=identity, when=playing_time, created=fixed_dt
    )
    assert expected_event in events_consumer.consume(2)


def test_marks_as_played(accepted_tracks, reset_events_fixt):
    requested = TrackRequested(ACCEPTED_TRACKS[0].identity, FUTURE_PT, Seconds(42))
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
    expected_event = TrackMarkedAsPlayed(
        identity=requested.identity, when=requested.when, created=fixed_dt
    )
    events = events_consumer.consume(2)
    assert expected_event in events


@mark.realdb()
def test_gets_tracks_count(accepted_tracks, pending_approval_tracks):
    playing_time = FUTURE_PT
    playlist.add(
        TrackRequested(PENDING_APPROVAL_TRACKS[0].identity, playing_time, Seconds(37))
    )
    playlist.add(
        TrackRequested(PENDING_APPROVAL_TRACKS[1].identity, playing_time, Seconds(28))
    )
    playlist.add(TrackRequested(ACCEPTED_TRACKS[0].identity, playing_time, Seconds(91)))

    assert playlist.get_tracks_count_on_break(playing_time, waiting=True) == 2
    assert playlist.get_tracks_count_on_break(playing_time, waiting=False) == 1
    assert playlist.get_tracks_count_on_break(playing_time) == 3


@mark.realdb()
def test_gets_tracks_duration(accepted_tracks, pending_approval_tracks):
    playing_time = FUTURE_PT
    track1 = PENDING_APPROVAL_TRACKS[0]
    track2 = PENDING_APPROVAL_TRACKS[1]
    track3 = ACCEPTED_TRACKS[0]

    playlist.add(TrackRequested(track1.identity, playing_time, Seconds(234)))
    playlist.add(TrackRequested(track2.identity, playing_time, Seconds(45)))
    playlist.add(TrackRequested(track3.identity, playing_time, Seconds(212)))

    sum_1_2 = sum([track1.duration or 0, track2.duration or 0])
    dur_3 = track3.duration or 0

    assert playlist.get_tracks_duration_on_break(playing_time, waiting=True) == sum_1_2
    assert playlist.get_tracks_duration_on_break(playing_time, waiting=False) == dur_3
    assert playlist.get_tracks_duration_on_break(playing_time) == sum_1_2 + dur_3


def test_checks_track_played_or_queued_this_day(accepted_tracks):
    identity = ACCEPTED_TRACKS[0].identity
    playing_time = FUTURE_PT
    requested = TrackRequested(identity, playing_time, Seconds(143))

    queued = playlist.add(requested)

    assert playlist.check_played_or_queued_on_day(identity, playing_time.date_) is True

    playlist.mark_as_played(queued)

    assert playlist.check_played_or_queued_on_day(identity, playing_time.date_) is True
