from kink import di
from pytest import fixture
from track.application.library import Library
from track.domain.entities import TrackRequested
from track.application.playlist import Playlist
from .data import FUTURE_PT, TRACKS

playlist = di[Playlist]
library = di[Library]


@fixture(autouse=True)
def reset():
    playlist_repo = playlist._playlist_repository
    library_repo = library._library_repository
    playlist_repo.delete_all()
    library_repo.delete_all()

    library_repo.add(TRACKS[0])

    yield

    playlist_repo.delete_all()
    library_repo.delete_all()


# def test_gets_tracks_only_not_played():


def test_adds_track_to_playlist():
    playing_time = FUTURE_PT
    requested = TrackRequested(TRACKS[0].identity, playing_time)

    playlist.add(requested)

    playlist_tracks_list = playlist.get_all(playing_time.date_)

    track_queued = playlist_tracks_list[0]
    assert track_queued.identity == requested.identity
    assert track_queued.when == playing_time


def test_marks_as_played():
    playing_time = FUTURE_PT
    requested = TrackRequested(TRACKS[0].identity, playing_time)
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
