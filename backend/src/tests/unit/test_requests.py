from datetime import date, datetime, timedelta
import pytest
from tests.unit.data import TRACKS, YT_TRACKS
from track.domain.errors import PlayingTimeError, TrackDurationExceeded
from track.application.playlist import Playlist
from track.domain.entities import NewTrack, Status, TrackRequested
from track.application.library import Library
from building_blocks.clock import SystemClock
from track.application.requests_service import RequestsService
from track.domain.breaks import Breaks, PlayingTime
from track.domain.provided import (
    Identifier,
    ProviderName,
    Seconds,
    TrackProvidedIdentity,
    TrackUrl,
)
from track.infrastructure.inmemory_library_repository import InMemoryLibraryRepository
from track.infrastructure.inmemory_playlist_repository import InMemoryPlaylistRepository


library_repo = InMemoryLibraryRepository()
playlist_repo = InMemoryPlaylistRepository()
system_clock = SystemClock()
library = Library(library_repo)
playlist = Playlist(playlist_repo)

rs = RequestsService(
    library_repo,
    playlist_repo,
    system_clock,
)


PASSED_PT = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2000, 1, 1),
)
FUTURE_PT = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2099, 1, 1),
)
FUTURE_PT_WEEKEND = PlayingTime(
    break_=Breaks.FIRST,
    date_=date(2099, 1, 3),
)


@pytest.fixture
def tracks():
    for track in TRACKS:
        library.add(track)


@pytest.fixture
def yt_tracks():
    for track in YT_TRACKS:
        library.add(track)


@pytest.fixture
def whole_break_scheduled():
    for track in TRACKS:
        req = TrackRequested(track.identity, FUTURE_PT)
        playlist.add_at(req, waiting=True)


@pytest.fixture(autouse=True)
def reset():
    playlist_repo._reset_state()
    library_repo._reset_state()

    yield

    playlist_repo._reset_state()
    library_repo._reset_state()


def test_adds_track_to_library_successfully():
    identity = YT_TRACKS[0].identity
    result, errors = rs.add_to_library(identity)
    assert result.added is True
    assert result.waits_on_decision is True
    assert len(errors) == 0

    got_track = library.get(identity)
    assert got_track is not None
    assert got_track.identity == identity


def test_too_long_track_not_added_to_library():
    identity = TrackProvidedIdentity(
        identifier=Identifier("c_iRx2Un07k"), provider=ProviderName("Youtube")
    )
    result, errors = rs.add_to_library(identity)
    assert result.added is False
    assert result.waits_on_decision is False
    assert len(errors) == 1
    assert isinstance(list(errors)[0], TrackDurationExceeded)


def test_no_provider_matched_for_track_requested():
    identity = TrackProvidedIdentity(
        identifier=Identifier("sth"), provider=ProviderName("notknownprovider")
    )
    with pytest.raises(RuntimeError) as ex:
        rs.add_to_library(identity)


def test_requests_to_add_already_pending_approval_track_in_library():
    identity = TrackProvidedIdentity(
        identifier=Identifier("a123"), provider=ProviderName("file")
    )
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
    track = YT_TRACKS[0]
    pt = PlayingTime(
        break_=Breaks.SECOND,
        date_=datetime.now().date() + timedelta(days=1),
    )
    rs.request_on(track.identity, pt)
    got_track = playlist.get(track.identity, pt.date_, pt.break_)
    assert got_track is not None
    assert got_track.when == pt


def test_error_as_requested_pt_passed(yt_tracks):
    track = YT_TRACKS[0]
    result = rs.request_on(track.identity, PASSED_PT)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(list(result.errors)[0], PlayingTimeError)


def test_error_as_requested_on_weekend(yt_tracks):
    track = YT_TRACKS[0]

    result = rs.request_on(track.identity, FUTURE_PT_WEEKEND)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(list(result.errors)[0], PlayingTimeError)


def test_error_as_track_played_on_this_day(yt_tracks):
    track = YT_TRACKS[0]
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
    assert isinstance(list(result.errors)[0], PlayingTimeError)


def test_error_as_track_already_queued_on_this_day(yt_tracks):
    track = YT_TRACKS[0]
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
    assert isinstance(list(result.errors)[0], PlayingTimeError)


@pytest.mark.skip()
def test_error_as_no_left_time_on_break(tracks, whole_break_scheduled):
    not_scheduled_track = YT_TRACKS[0]
    result = rs.request_on(not_scheduled_track.identity, FUTURE_PT)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(list(result.errors)[0], PlayingTimeError)


def test_error_as_max_queue_count_exceeded(tracks):
    pass


@pytest.mark.skip()
def test_multiple_playlist_errors(tracks, whole_break_scheduled):
    scheduled_track = TRACKS[0]
    result = rs.request_on(scheduled_track.identity, FUTURE_PT)
    assert result.success is False
    assert result.errors is not None
    assert isinstance(list(result.errors)[0], PlayingTimeError)
    assert isinstance(list(result.errors)[1], PlayingTimeError)
