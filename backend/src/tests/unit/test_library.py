from pytest import fixture
from tests.unit.data import TRACKS
from track.application.library import Library
from track.domain.entities import Status
from track.infrastructure.inmemory_library_repository import (
    InMemoryLibraryRepository,
)


library_repo = InMemoryLibraryRepository()
library = Library(library_repo)


@fixture()
def tracks_one_accepted():
    for track in TRACKS:
        library.add(track)

    library.accept(TRACKS[0].identity)


@fixture(autouse=True)
def reset():
    library_repo.delete_all()

    yield

    library_repo.delete_all()


def test_new_track_has_pending_approval_state():
    track = TRACKS[0]
    library.add(track)
    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.PENDING_APPROVAL


def test_accept_track():
    track = TRACKS[0]
    library.add(track)

    library.accept(track.identity)

    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.ACCEPTED


def test_reject_track():
    track = TRACKS[0]
    library.add(track)

    library.reject(track.identity)

    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.REJECTED


def test_filters_tracks_by_status(tracks_one_accepted):
    tracks_filtered = library.filter_by_statuses(
        [Status.PENDING_APPROVAL, Status.ACCEPTED]
    )
    assert len(tracks_filtered) == 3
    assert len(library.filter_by_statuses([Status.PENDING_APPROVAL])) == 2
