from kink import di
from pytest import fixture

from building_blocks.clock import Clock
from tests.helpers.dt import fixed_dt
from tests.unit.data import ACCEPTED_TRACKS, NEW_TRACKS, PENDING_APPROVAL_TRACKS
from track.application.library import Library
from track.domain.entities import Status
from track.domain.events.library import TrackAddedToLibrary
from track.infrastructure.messaging.types import LibraryEventsConsumer

library = di[Library]
library_repo = library._library_repository
events_consumer = di[LibraryEventsConsumer]
events_producer = library._events_producer
clock = di[Clock]


@fixture()
def reset():
    library_repo.delete_all()

    yield

    library_repo.delete_all()


@fixture()
def tracks_one_accepted(reset):
    library_repo.add(PENDING_APPROVAL_TRACKS[0])
    library_repo.add(ACCEPTED_TRACKS[0])


def test_new_track_has_pending_approval_state(reset, reset_events_fixt):
    events_consumer.seek_beginning()
    track = NEW_TRACKS[0]
    library.add(track)
    got_track = library.get(track.identity)
    assert got_track is not None
    assert got_track.status == Status.PENDING_APPROVAL
    expected_event = TrackAddedToLibrary(identity=track.identity, created=fixed_dt)
    assert expected_event in events_consumer.consume(1)


def test_filters_tracks_by_status(tracks_one_accepted):
    tracks_filtered = library.filter_by_statuses(
        [Status.PENDING_APPROVAL, Status.ACCEPTED]
    )
    assert len(tracks_filtered) == 2
    assert len(library.filter_by_statuses([Status.PENDING_APPROVAL])) == 1
