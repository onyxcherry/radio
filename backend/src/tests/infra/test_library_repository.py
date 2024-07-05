from pytest import fixture

from track.domain.entities import Status
from track.infrastructure.db_library_repository import DBLibraryRepository
from tests.infra.data import IDENTITIES, TRACKS


library_repo = DBLibraryRepository()


@fixture(autouse=True)
def reset():
    library_repo.delete_all()

    library_repo.add(TRACKS[0])

    yield

    library_repo.delete_all()


def test_adds_track():
    new_track = TRACKS[1]
    library_repo.add(new_track)

    got_track = library_repo.get(new_track.identity)
    assert got_track is not None
    assert got_track.identity == new_track.identity


def test_gets_track():
    identity = IDENTITIES[0]
    got_track = library_repo.get(identity)
    assert got_track is not None
    assert got_track.identity == identity


def test_filters_accepted_tracks():
    filtered = library_repo.filter_by_statuses([Status.ACCEPTED])
    assert filtered is not None
    assert len(filtered) == 1
    assert filtered[0].identity == IDENTITIES[0]


def test_filters_pending_approval_tracks():
    filtered = library_repo.filter_by_statuses([Status.PENDING_APPROVAL])
    assert filtered is not None
    assert len(filtered) == 0


def test_filters_by_mutliple_statuses_of_tracks():
    filtered = library_repo.filter_by_statuses(
        [Status.ACCEPTED, Status.PENDING_APPROVAL]
    )
    assert filtered is not None
    assert len(filtered) == 1


def test_updates_status():
    track_to_update = TRACKS[0]
    new_status = Status.REJECTED
    track_to_update.status = new_status
    result = library_repo.update(track_to_update)

    assert result == track_to_update
    got = library_repo.get(track_to_update.identity)
    assert got is not None
    assert got.status == new_status
