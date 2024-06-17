from datetime import timedelta
from kink import di
from pytest import fixture
from building_blocks.clock import Clock
from track.domain.breaks import Breaks, PlayingTime
from track.domain.entities import TrackRequested
from track.application.playlist import Playlist
from track.infrastructure.inmemory_playlist_repository import InMemoryPlaylistRepository
from .data import TRACKS

playlist_repo = InMemoryPlaylistRepository()
playlist = Playlist(playlist_repo)
clock = di[Clock]

track = TRACKS[0]
tomorrow_date = clock.get_current_date() + timedelta(days=1)
playing_time = PlayingTime(tomorrow_date, Breaks.SECOND)
requested = TrackRequested(track.identity, playing_time)


@fixture(autouse=True)
def reset():
    playlist_repo._reset_state()

    yield

    playlist_repo._reset_state()


# def test_gets_tracks_only_not_played():


def test_adds_track_to_playlist():
    track = TRACKS[0]
    tomorrow_date = clock.get_current_date() + timedelta(days=1)
    playing_time = PlayingTime(tomorrow_date, Breaks.SECOND)
    request = TrackRequested(track.identity, playing_time)

    playlist.add_at(request, waiting=False)

    playlist_tracks_list = playlist.get_all(playing_time.date_)

    track_queued = playlist_tracks_list[0]
    assert track_queued.identity == track.identity
    assert track_queued.when == playing_time


def test_marks_as_played():
    playlist.add_at(requested, waiting=False)

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
