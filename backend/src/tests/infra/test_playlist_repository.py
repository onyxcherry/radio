from datetime import date
from pytest import fixture
from track.domain.entities import TrackQueued, TrackToQueue
from tests.infra.data import IDENTITIES, TRACKS
from track.infrastructure.db_library_repository import DBLibraryRepository
from track.infrastructure.db_playlist_repository import DBPlaylistRepository
from track.domain.breaks import Breaks, PlayingTime


# playlist_repo = di[PlaylistRepository]
# library_repo = di[LibraryRepository]

playlist_repo = DBPlaylistRepository()
library_repo = DBLibraryRepository()


TRACK_QUEUED = TrackToQueue(
    identity=IDENTITIES[0],
    when=PlayingTime(date_=date(2099, 1, 1), break_=Breaks.FIRST),
    played=False,
)


@fixture(autouse=True)
def reset():
    playlist_repo.delete_all()
    library_repo.delete_all()

    library_repo.add(TRACKS[0])
    library_repo.add(TRACKS[1])

    playlist_repo.insert(TRACK_QUEUED)

    yield

    playlist_repo.delete_all()
    library_repo.delete_all()


def test_gets_track():
    result = playlist_repo.get_track_on(
        identity=TRACK_QUEUED.identity,
        date_=TRACK_QUEUED.when.date_,
        break_=TRACK_QUEUED.when.break_,
    )
    assert result is not None
    assert result.identity == TRACK_QUEUED.identity
    assert result.when.date_ == TRACK_QUEUED.when.date_
    assert result.when.break_ == TRACK_QUEUED.when.break_


def test_gets_all_tracks():
    result = playlist_repo.get_all(
        date_=TRACK_QUEUED.when.date_,
        break_=TRACK_QUEUED.when.break_,
    )
    assert result is not None
    assert len(result) == 1
    assert result[0].identity == TRACK_QUEUED.identity
    assert result[0].when.date_ == TRACK_QUEUED.when.date_
    assert result[0].when.break_ == TRACK_QUEUED.when.break_


def test_counts_tracks():
    result = playlist_repo.count_on(
        date_=TRACK_QUEUED.when.date_, break_=TRACK_QUEUED.when.break_
    )
    assert result == 1


def test_gets_sum_of_durations():
    result = playlist_repo.sum_durations_on(
        date_=TRACK_QUEUED.when.date_, break_=TRACK_QUEUED.when.break_
    )
    assert result == 189


def test_adds_track_to_playlist():
    playing_time = PlayingTime(date_=date(2099, 1, 1), break_=Breaks.FIRST)
    new_queued_track = TrackToQueue(
        identity=IDENTITIES[1], when=playing_time, played=False
    )

    playlist_repo.insert(new_queued_track)
    result = playlist_repo.get_track_on(
        identity=new_queued_track.identity,
        date_=playing_time.date_,
        break_=playing_time.break_,
    )
    assert result is not None
    assert result.identity == new_queued_track.identity


def test_deletes_track_from_queue():
    result = playlist_repo.delete(TRACK_QUEUED)
    assert result is not None
    assert result.identity == TRACK_QUEUED.identity


def test_deletes_all_tracks_from_queue():
    result = playlist_repo.delete_all()
    assert result == 1
